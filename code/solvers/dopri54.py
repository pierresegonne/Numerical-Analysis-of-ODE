import numpy as np

from solvers.utils import parse_adaptive_step_params, rk_step

# Butcher Tableau
C = np.array([0, 1/5, 3/10, 4/5, 8/9, 1, 1])
A = np.array([
    [0, 0, 0, 0, 0, 0, 0],
    [1/5, 0, 0, 0, 0, 0, 0],
    [3/40, 9/40, 0, 0, 0, 0, 0],
    [44/45, -56/15, 32/9, 0, 0, 0, 0],
    [19372/6561, -25360/2187, 64448/6561, -212/729, 0, 0, 0],
    [9017/3168, -355/33, 46732/5247, 49/176, -5103/18656, 0, 0],
    [35/384, 0, 500/1113, 125/192, -2187/6784, 11/84, 0],
])
B_hat = np.array([5179/57600, 0, 7571/16695, 393/640, -92097/339200, 187/2100,
              1/40])
B = np.array([35/384, 0, 500/1113, 125/192, -2187/6784, 11/84, 0])
E = B - B_hat


# Order
P_DOPRI54 = 5


def dopri54_step(f, t, x, dt, **kwargs):

    butcher_tableau = {
        'A': A,
        'B': B,
        'C': C,
        'E': E,
    }

    return rk_step(f, t, x, dt, butcher_tableau, **kwargs)


def ode_solver(f, J, t0, tf, N, x0, adaptive_step_size=False, **kwargs):

    dt = (tf - t0)/N

    T = [t0]
    X = [x0]
    controllers = {
        'r': [0.01],
        'e': [np.zeros(x0.shape)],
        'dt': [dt],
    }

    if not adaptive_step_size:

        for k in range(N):
            x, e = dopri54_step(f, T[-1], X[-1], dt, **kwargs)
            X.append(x)
            T.append(T[-1] + dt)
            controllers['e'].append(e)

    if adaptive_step_size:

        kwargs, abstol, reltol, epstol, facmax, facmin = parse_adaptive_step_params(kwargs)
        p = P_DOPRI54
        k_p = 0.4/(p+1)
        k_i = 0.3/(p+1)

        t = t0
        x = x0

        while t < tf:
            if (t + dt > tf):
                dt = tf - t

            accept_step = False
            while not accept_step:
                x_hat, e = dopri54_step(f, T[-1], X[-1], dt, **kwargs)
                r = np.max(np.abs(e) / np.maximum(abstol, np.abs(x_hat)*reltol))

                accept_step = (r <= 1)
                if accept_step:
                    t = t + dt
                    x = x_hat
                    dt = dt * np.maximum(facmin, np.minimum((epstol/r)**(k_i) * (controllers['r'][-1]/r)**(k_p), facmax))

                    T.append(t)
                    X.append(x)
                    controllers['e'].append(e)
                    controllers['r'].append(r)
                else:
                    dt = np.maximum(facmin, np.minimum((epstol / r)**(1 / (p + 1)), facmax)) * dt
                controllers['dt'].append(dt)


    T = np.array(T)
    X = np.array(X)
    controllers['dt'] = np.array(controllers['dt'])
    controllers['r'] = np.array(controllers['r'])
    controllers['e'] = np.array(controllers['e'])

    return X, T, controllers
