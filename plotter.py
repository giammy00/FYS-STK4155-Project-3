import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms
import matplotlib as mlt

figsize = (3.313, 3)
plt.rc('text', usetex=True)
plt.rc('font', family='serif')

def plot_eigenvector_components_convergence(time, time_evolution_array):
    """
    Takes the time evolution of the point and plots the path for each component.

    args:
        time: array (or tensor) containing N timesteps
        time_evolution_array: np.ndarray (or tf.Tensor) of shape (dim, N), dim=dimension of space.
    """
    fig = plt.figure(figsize=figsize)
    plt.xlabel('t')
    plt.ylabel('Eigenvector Components')

    for component in time_evolution_array:
        plt.plot(time, component, lw=2, zorder=1)
        plt.grid(visible=True)

    return fig

def plot_mean_squared_error(epochs, epoch_evolution_array):
    """
    Takes the evolution of the mean squared error with respect to
    the number of epochs and plots it
    """
    fig = plt.figure(figsize=figsize)
    plt.xlabel('N_{epochs}')
    plt.ylabel('MSE')
    plt.plot(epochs, epoch_evolution_array, zorder=1, lw=2)
    plt.grid(visible=True)
    return fig

def plot_estimated_eigenvetors(epochs, final_eigenvect_evolution):

    fig = plt.figure(figsize=figsize)
    plt.xlabel('N_{epochs}')
    plt.ylabel('Eigenvector Components')

    for component in final_eigenvect_evolution:
        plt.plot(epoch, component, zorder=1, lw=2)
        plt.grid(visible=True)
    return fig

def true_solution(x, t):
    return np.exp(-t*np.pi**2)*np.sin(x*np.pi)

def plot_fd_solutions(u, x, t, t1_index, t2_index):

    high_def_x = np.linspace(0, 1, 1000)
    true1 = true_solution(high_def_x, t[t1_index])
    true2 = true_solution(high_def_x, t[t2_index])

    t1 = f't = {t[t1_index]:.2f}'
    t2 = f't= {t[t2_index]:.2f}'

    fig, (true_v_fd, error_plot) = plt.subplots(1, 2, figsize=(figsize[0]*2, figsize[1]))
    fig.set_tight_layout(True)

    true_v_fd.grid()
    error_plot.grid()

    true_v_fd.set_xlabel('x')
    true_v_fd.set_ylabel('T')

    true_v_fd.plot(high_def_x, true1, color='blue', label='True solutions')
    true_v_fd.plot(high_def_x, true2, color='blue')
    true_v_fd.plot(x, u[t1_index, :], label = t1)
    true_v_fd.plot(x, u[t2_index, :], label = t2)

    error_1 = abs(true_solution(x, t[t1_index])-u[t1_index, :])/true_solution(x, t[t1_index])
    error_2 = abs(true_solution(x, t[t2_index])-u[t2_index, :])/true_solution(x, t[t2_index])

    error_plot.set_xlabel('x')
    error_plot.set_ylabel('Absolute Relative Error')

    error_plot.plot(x, error_1, label=t1)
    error_plot.plot(x, error_2, label=t2)

    plt.legend()

    return fig

def plot_resolution(dx, mean_error):

    fig = plt.figure(figsize=figsize)
    fig.set_tight_layout(True)
    plt.xlabel('\Delta{x}')
    plt.ylabel('Mean Squared Error')

    plt.plot(dx, mean_error)

    return fig

def plot_NN_losses(losses):
    
    fig = plt.figure(figsize=figsize)
    fig.set_tight_layout(True)
    plt.plot(losses)
    plt.yscale("log")
    plt.xlabel("Training time")
    plt.ylabel("Training loss")
    
    return fig