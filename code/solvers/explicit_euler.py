import numpy as np

DEFAULT_ABS_TOL = 1e-6
DEFAULT_REL_TOL = 1e-6
DEFAULT_EPS_TOL = 0.8
DEFAULT_FACTOR_MAX = 5
DEFAULT_FACTOR_MIN = 0.1

def parse_one_adaptive_step_param(params, param_name, param_default_value):
    if param_name in params.keys():
        param = params[param_name]
        del params[param_name]
    else:
        param = param_default_value
    return params, param

def parse_adaptive_step_params(params):

    params, abstol = parse_one_adaptive_step_param(params, 'abstol', DEFAULT_ABS_TOL)
    params, reltol = parse_one_adaptive_step_param(params, 'reltol', DEFAULT_REL_TOL)
    params, epstol = parse_one_adaptive_step_param(params, 'epstol', DEFAULT_EPS_TOL)
    params, facmax = parse_one_adaptive_step_param(params, 'facmax', DEFAULT_FACTOR_MAX)
    params, facmin = parse_one_adaptive_step_param(params, 'facmin', DEFAULT_FACTOR_MIN)

    return params, abstol, reltol, epstol, facmax, facmin

def ode_solver(f, J, t0, tf, N, x0, adaptive_step_size=False, **kwargs):

    dt = (tf - t0)/N

    T = [t0]
    X = [x0]

    if not adaptive_step_size:

        for k in range(N):
            f_eval = f(T[-1], X[-1], **kwargs)
            X.append(X[-1] + dt*f_eval)
            T.append(T[-1] + dt)

    if adaptive_step_size:

        kwargs, abstol, reltol, epstol, facmax, facmin = parse_adaptive_step_params(kwargs)
        print(kwargs, abstol, reltol, epstol, facmax, facmin)
        exit()

        t = t0
        x = x0

        while t < tf:
            if (t + dt > tf):
                dt = tf - t

            f_eval = f(t, x, **kwargs)

            accept_step = False
            while not accept_step:
                # Take step of size dt
                x_1 = x + dt*f_eval

                # Take two steps of size dt/2
                x_hat_12 = x + (dt/2)*f_eval
                t_hat_12 = t + (dt/2)
                f_eval_12 = f(t_hat_12, x_hat_12, **kwargs)
                x_hat = x_hat_12 + (dt/2)*f_eval_12

                # Error estimation
                e = np.abs(x_1 - x_hat)
                r = np.max(e / np.maximum(abstol, np.abs(x_hat)*reltol))

                accept_step = (r <= 1)
                if accept_step:
                    t = t + dt
                    x = x_hat

                    T.append(t)
                    X.append(x)

                dt = np.maximum(facmin, np.minimum(np.sqrt(epstol/r), facmax)) * dt

    T = np.array(T)
    X = np.array(X)

    return X, T

