import tensorflow as tf


def get_envelop(args):
    if args.envelop_form == 'tanh':
        return tf.tanh
    elif args.envelop_form == 'polynomial' or args.envelop_form == 'hill':
        k = args.polynomial_k
        if k%2 == 1: # odd Hill equation
            return lambda x: x**k/(1+tf.abs(x)**k)
        else: # even Hill equation
            return lambda x: x**k/(1+x**k)*tf.sign(x)
    else:
        raise Exception("Illegal envelop function. Choose from [tanh, polynomial/hill]")

def get_dXdt(args, envelop):

    if args.ode_degree == 1:
        weighted_sum = lambda x: tf.matmul(envelop.W, x)
    elif args.ode_degree == 2:
        weighted_sum = lambda x: tf.matmul(envelop.W, x) * x
    else:
        raise Exception("Illegal ODE degree. Choose from [1,2].")

    if args.envelop == 0:
        # epsilon*phi(Sigma+u)-alpha*x
        return lambda x, t_mu, envelop: envelop.eps * envelop(weighted_sum(x) + t_mu) - envelop.alpha * x
    elif args.envelop == 1:
        # epsilon*[phi(Sigma)+u]-alpha*x
        return lambda x, t_mu, envelop: envelop.eps * (envelop(weighted_sum(x)) + t_mu) - envelop.alpha * x
    elif args.envelop == 2:
        # epsilon*phi(Sigma)+psi*u-alpha*x
        psi = tf.Variable(np.ones((n_x, 1)), name="psi", dtype=tf.float32)
        return lambda x, t_mu, envelop: envelop.eps * envelop(weighted_sum(x)) + envelop.psi*t_mu - envelop.alpha * x
    else:
        raise Exception("Illegal envelop type. Choose from [1,2,3].")

def get_ode_solver(args):
    if args.ode_solver == 'heun':
        return heun_solver
    elif args.ode_solver == 'euler':
        return euler_solver
    elif args.ode_solver == 'rk4':
        return rk4_solver
    elif args.ode_solver == 'midpoint':
        return midpoint_solver
    else:
        raise Exception("Illegal ODE solver. Use [heun, euler, rk4, midpoint]")

def heun_solver(x, t_mu, dT, n_T, envelop, _dXdt, args):
    xs = x
    for i in range(n_T):
        dXdt_current = _dXdt(x, t_mu, envelop)
        dXdt_next = _dXdt(x + dT * dXdt_current, t_mu, envelop)
        x = x + dT * 0.5 * (dXdt_current + dXdt_next)
        xs = tf.concat([xs, x], axis = 0)
    return xs

def euler_solver(x, t_mu, dT, n_T, envelop, _dXdt, args):
    xs = x
    for i in range(n_T):
        dXdt_current = _dXdt(x, t_mu, envelop)
        x = x + dT * dXdt_current
        xs = tf.concat([xs, x], axis = 0)
    return xs

def midpoint_solver(x, t_mu, dT, n_T, envelop, _dXdt, args):
    xs = x
    for i in range(n_T):
        dXdt_current = _dXdt(x, t_mu, envelop)
        dXdt_midpoint = _dXdt(x + 0.5 * dT * dXdt_current, t_mu, envelop)
        x = x + dT * dXdt_midpoint
        xs = tf.concat([xs, x], axis = 0)
    return xs

def rk4_solver(x, t_mu, dT, n_T, envelop, _dXdt, args):
    xs = x
    for i in range(n_T):
        k1 = _dXdt(x, t_mu, envelop)
        k2 = _dXdt(x + 0.5*dT*k1, t_mu, envelop)
        k3 = _dXdt(x + 0.5*dT*k2, t_mu, envelop)
        k4 = _dXdt(x + dT*k3, t_mu, envelop)
        x = x + dT * (1/6*k1+1/3*k2+1/3*k3+1/6*k4)
        xs = tf.concat([xs, x], axis = 0)
    return xs