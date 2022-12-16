import eigenSolverNN as esnn
import numpy as np
import tensorflow as tf
import warnings

def normalized_proj(vector1, vector2):
    '''computes the projection of vector1 along the direction specified by vector2.
       With dirac's notation this is equivalent to ( <v2|v1>/<v2|v2> ) |v2>.
    '''
    normalization = np.dot(vector1, vector2)/np.dot(vector2, vector2)
    return normalization*vector2

def create_orthogonal(vectors_array):
    """
    Creates a random vector and substracts all components parallel to
    the vectors in vectors_array. These vectors belong to R^n .

    returns:
    orthogonal_vector: vector such that the dot product
         orthogonal_vector * vectors_array[ii] = 0 for all ii.
        IMPORTANT NOTE: this is true under the assumption that vectors_array is an orthogonal set.
        Note that this will be the 0 vector if there are more than n vectors in vectors_array .
    """
    n = len(vectors_array[0]) #size of vectors
    orthogonal_vector = np.random.randn(n)

    # Gram-Schmidt algorithm
    for vector in vectors_array:
        orthogonal_vector -= normalized_proj(orthogonal_vector, vector)

    return orthogonal_vector/np.linalg.norm(orthogonal_vector)

def check_eig(eigval, eigvec, A):
    '''check that eigvec is an eigenvector of A with eigenvalue eigval.
    All args must be given as tf.Tensor() instances, and are converted to numpy here.
    '''

    eigval = eigval.numpy()
    eigvec = eigvec.numpy()
    A = A.numpy()

    #lambdavec should have components all equal to eigval
    lambdavec = (A@eigvec.T)/eigvec.T
    #dividing by eigval should give a vector of ones
    ones_vec = lambdavec/eigval
    print(ones_vec)
    #check that this vector is close enough to np.ones()
    A = np.allclose(ones_vec, np.ones(ones_vec.shape), rtol=0.2)
    if not A:
        warnings.warn(f"eigenvector ({eigvec}) might not be an eigenvector of A.")
    return A

def findEigenvectors(A):
    '''
    Find all eigenvectors of matrix A, using neural net.

    '''
    n = A.shape[0]

    eigenvectors = np.zeros((n,n))
    eigenvalues = np.zeros(n)

    starting_point = tf.random.normal([n], dtype='float64')

    #initialize instance of solver
    Nepochs = 50000
    Nbatches = 4

    for i in range(n):
        print(f"### FINDING EIGENVECTOR NR.{i} ###\n")
        solver = esnn.eigSolverNN(A, starting_point)
        solver.train_model(Nepochs, Nbatches)
        eigenvalue, eigvector = solver.compute_eig()

        #SHOULD CHECK THAT WHAT WE HAVE GOTTEN SO FAR *IS* AN EIGENVECTOR.
        #OTHERWISE, TRAINING AGAIN WOULD NOT MAKE SENSE
        check_eig(eigenvalue, eigvector, A)


        eigenvectors[i] = eigvector
        eigenvalues[i] = eigenvalue
        starting_point = create_orthogonal(eigenvectors[:i+1, :])

    return eigenvectors, eigenvalues

def Many_Random_Points(number_of_points, A, learning_rate, tolerance=0.1, Nepochs=int(1e5), Nbatches=4):
    dimension = A.shape[0]
    class_instances = []

    eigenvalues = []
    eigenvectors =[]

    unique_eigenvalues = []
    unique_eigenvectors = []

    for _ in range(number_of_points):
        x0 = tf.random.normal([dimension], dtype='float64')
        neural_net_solver = esnn.eigSolverNN(A, x0)
        neural_net_solver.optimizer.lr.assign(learning_rate)
        class_instances.append(
            neural_net_solver
        )

    for i, neural_net_solver in enumerate(class_instances):
        neural_net_solver.train_model(Nepochs, Nbatches, tolerance=tolerance)
        eigval, eigvec = neural_net_solver.compute_eig()
        if check_eig(eigval, eigvec, A):
            eigenvalues[i], eigenvectors[i] = eigval, eigvec

    for i, eigval in enumerate(eigenvalues):
        condition = abs((np.array(unique_eigenvalues)-eigval))<(0.2*eigval)
        if not np.any(condition):
            unique_eigenvalues.append(eigval)

    return unique_eigenvalues

def Search_Until_Find(A):
    '''
    Find all eigenvectors of matrix A, using neural net.

    '''
    n = A.shape[0]

    eigenvectors = []
    eigenvalues = []

    starting_point = tf.random.normal([n], dtype='float64')

    #initialize instance of solver
    Nepochs = 50000
    Nbatches = 4
    repeat_counter = 0

    while len(eigenvalues) < 6:
        print(f"### FINDING EIGENVECTOR NR.{len(eigenvalues)} ###\n")
        solver = esnn.eigSolverNN(A, starting_point)
        solver.train_model(Nepochs, Nbatches)
        eigenvalue, eigvector = solver.compute_eig()

        #SHOULD CHECK THAT WHAT WE HAVE GOTTEN SO FAR *IS* AN EIGENVECTOR.
        #OTHERWISE, TRAINING AGAIN WOULD NOT MAKE SENSE
        if check_eig(eigenvalue, eigvector, A):
            if not np.any(abs(np.array(eigenvalues)-eigenvalue)<0.01):
                print(f'Found new eigenvector: \n {eigvector} \n eigenvalue {eigenvalue}')

                #remove orthognality with other eigenvectors
                for vec in eigenvectors:
                    eigvector -= normalized_proj(eigvector, vec)

                eigenvalues.append(eigenvalue[0])
                eigenvectors.append(eigvector[0])
                repeat_counter = 0
            else:
                print(f'Duplicate {eigenvalue}')
                repeat_counter += 1
        else:
            print(f'Found something not an eigenvector of A: \n {eigvector}')
        starting_point = tf.random.normal([n], mean=0. , stddev=1+repeat_counter, dtype='float64')

        for vec in eigenvectors:
            starting_point -= normalized_proj(starting_point, vec)

    return eigenvectors, eigenvalues

if __name__ == '__main__':
    A = np.load('A.npy')
    A = tf.convert_to_tensor(A)
    #eigenvalues = Many_Random_Points(15, A, 0.0175, tolerance=1e-7, Nepochs=40000)
    eigenvectors, eigenvalues = Search_Until_Find(A)
    print(eigenvalues)
    A = A.numpy()
    [E, V] = np.linalg.eigh(A)
    print(E)
