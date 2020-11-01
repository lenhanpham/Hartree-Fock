##################################################################################
# This Hartree-Fock program is written for the purposes of self learning Python
# This program is to solve the Schrodinger equation for HHe+
# All the codes are written using algorithms and instructions in
# the Szabo's and Neil's book: Modern quantum chemistry (1989)
#
# Author: LE NHAN PHAM
#        Department of Chemistry Dalat University, Vietnam
#        Department of Chemistry KU LEUVEN, Belgium
#
##################################################################################

import numpy as np
import math

# import scipy.special as sp # uncomment this module for use of special functions such as erf(t)


def MAIN():
    N = 3
    Z_H = 1
    Z_He = 2
    R = 1.4632
    Zeta1 = 2.0925
    Zeta2 = 1.24
    HFCALC(N, R, Zeta1, Zeta2, Z_H, Z_He)


#########################
# Integrals
#########################

##### One-electron integrals: overlap integrals#####


def OverLap_S_int(Alpha, Beta, R2_ab):
    ## Alpha and Beta are the exponents of primitive Gaussian functions
    ## R2_ab is the square of distance between two Gaussian functions

    """
    Calculate the overlap integrals between two gaussian funtions 

    """
    return (np.pi / (Alpha + Beta) ** 1.5) * np.exp(
        (-Alpha * Beta / (Alpha + Beta) * R2_ab)
    )


def Kinetic_T_int(Alpha, Beta, R2_ab):
    ## All variables are the same as in overlap integral functions

    """
    Calculate the kinetic integrals of electrons 
    """

    return (
        Alpha
        * Beta
        / (Alpha + Beta)
        * (
            3.0
            - (2.0 * Alpha * Beta / (Alpha + Beta) * R2_ab)
            * np.pi
            / (Alpha + Beta) ** 1.5
            * np.exp(-Alpha * Beta * R2_ab / (Alpha + Beta))
        )
    )


def Potential_V_int(Alpha, Beta, Zc, R2_ab, R2_pc):
    """
    Calculate the potential integrals of electrons caused by nuclei of atoms
    """
    ## All variables are defined as in the overlap integral function
    ## R2_pc is the square of distance from a product Gaussian function generated by
    # two Gaussian functions to one of the original ones

    return (
        -2.0
        * np.pi
        / (Alpha + Beta)
        * Zc
        * np.exp(-Alpha * Beta * R2_ab / (Alpha + Beta))
        * F0((Alpha + Beta) * R2_pc)
    )


#### Define Functions used to calculate Potential and two-electron integrals######


def F0(t):
    """
    F function for calculation of potential integrals and two-electron integrals
    """

    if t < 1e-6:  ## Approximate value of F0 for the case of too small t
        return 1.0 - t / 3.0
    else:
        return 0.5 * (np.pi / t) ** 0.5 * erf(t ** 0.5)


def erf(t):
    """ 
    Numerical approximation of the error function to 3e-7
    """
    P = 0.3275911
    A = [0.254829592, -0.284496736, 1.421413741, -1.453152027, 1.061405429]
    T = 1.0 / (1 + P * t)
    Polynomial = 0.0
    for i in range(5):
        Polynomial = Polynomial + A[i] * np.power(T, i + 1)
    return 1.0 - Polynomial * np.exp(-t * t)


def TwoE_int(Alpha, Beta, Gamma, Delta, R2_ab, R2_cd, R2_pq):
    """
    Calculate two electron integrals
    """
    ## Alpha, Beta, Gamma, and Delta are exponents of primitive Gaussian functions

    return (
        2.0
        * np.pi ** 2.5
        / ((Alpha + Beta) * (Gamma + Delta) * np.sqrt(Alpha + Beta + Gamma + Delta))
        * np.exp(
            -Alpha * Beta * R2_ab / (Alpha + Beta)
            - Gamma * Delta * R2_cd / (Gamma + Delta)
        )
        * F0((Alpha + Beta) * (Gamma + Delta) * R2_pq / (Alpha + Beta + Gamma + Delta))
    )


### Calculate electron integrals in terms of basis functions which are linear combinations
# of primitive Gaussian functions


def AO_Integral(N, R, Zeta1, Zeta2, Z_H, Z_He):
    """
    Calculate integals of basis fucntions (AOs)
    """
    ## N is the level of STO-nG; Zeta1 and Zeta2 are the exponents of Slater Orbitals
    # of H and He; Za and Zb are the atomic number of H and He

    (
        S12,
        T11,
        T12,
        T22,
        V11H,
        V12H,
        V22H,
        V11He,
        V12He,
        V22He,
        V1111,
        V2111,
        V2121,
        V2211,
        V2221,
        V2222,
    ) = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    R2 = R * R

    # The coefficients and exponents of primitive Gaussian functions for three levels
    # of STO-nG (n =1,2,3) with Zeta = 1.0
    Coefft = np.array(
        [
            [1.00000, 0.0000000, 0.000000],
            [0.678914, 0.430129, 0.000000],
            [0.444635, 0.535328, 0.154329],
        ]
    )

    Expont = np.array(
        [
            [0.270950, 0.000000, 0.000000],
            [0.151623, 0.851819, 0.000000],
            [0.109818, 0.405771, 2.227660],
        ]
    )

    # Generate coefficients and exponents of the STO-nG for two atoms H and He
    Coe_H1s = np.zeros(3)
    Exp_H1s = np.zeros(3)
    Coe_He1s = np.zeros(3)
    Exp_He1s = np.zeros(3)

    # Construct the contracted Gaussian functions for each atoms scaling up with its Slater exponent
    for i in range(N):
        Exp_H1s[i] = Expont[N - 1, i] * (Zeta1 ** 2)
        Exp_He1s[i] = Expont[N - 1, i] * (Zeta2 ** 2)
        Coe_H1s[i] = Coefft[N - 1, i] * ((2.0 * Exp_H1s[i] / np.pi) ** 0.75)
        Coe_He1s[i] = Coefft[N - 1, i] * ((2.0 * Exp_He1s[i] / np.pi) ** 0.75)

    # Calculate AO integrals by summation of all primitive Gaussian integrals

    for i in range(N):
        for j in range(N):
            # Calculate the distance between center P of the product Gaussian function and centers
            # A and B of the original primitive ones
            R_ap = Exp_He1s[j] * R / (Exp_H1s[i] + Exp_He1s[j])
            R2_ap = R_ap ** 2
            R2_bp = (R - R_ap) ** 2

            # Calculate accumulative integrals between AOs (linear combination of primitive Gaussian functions)
            S12 = (
                S12
                + OverLap_S_int(Exp_H1s[i], Exp_He1s[j], R2) * Coe_H1s[i] * Coe_He1s[j]
            )
            T11 = (
                T11
                + Kinetic_T_int(Exp_H1s[i], Exp_H1s[j], 0.0) * Coe_H1s[i] * Coe_H1s[j]
            )
            T12 = (
                T12
                + Kinetic_T_int(Exp_H1s[i], Exp_He1s[j], R2) * Coe_H1s[i] * Coe_He1s[j]
            )
            T22 = (
                T22
                + Kinetic_T_int(Exp_He1s[i], Exp_He1s[j], 0.0)
                * Coe_He1s[i]
                * Coe_He1s[j]
            )

            # Z_H and Z_He are atomic numbers of H and He provided from the input
            V11H = (
                V11H
                + Potential_V_int(Exp_H1s[i], Exp_H1s[j], Z_H, 0.0, 0.00)
                * Coe_H1s[i]
                * Coe_H1s[j]
            )
            V12H = (
                V12H
                + Potential_V_int(Exp_H1s[i], Exp_He1s[j], Z_H, R2, R2_ap)
                * Coe_H1s[i]
                * Coe_He1s[j]
            )
            V22H = (
                V22H
                + Potential_V_int(Exp_He1s[i], Exp_He1s[j], Z_H, 0.0, R2)
                * Coe_He1s[i]
                * Coe_He1s[j]
            )

            V11He = (
                V11He
                + Potential_V_int(Exp_H1s[i], Exp_H1s[j], Z_He, 0.0, R2)
                * Coe_H1s[i]
                * Coe_H1s[j]
            )
            V12He = (
                V12He
                + Potential_V_int(Exp_H1s[i], Exp_He1s[j], Z_He, R2, R2_bp)
                * Coe_H1s[i]
                * Coe_He1s[j]
            )
            V22He = (
                V22He
                + Potential_V_int(Exp_He1s[i], Exp_He1s[j], Z_He, 0.0, 0.0)
                * Coe_He1s[i]
                * Coe_He1s[j]
            )

    # Calculate two-electron integrals using AOs which are linear combinations of primitive Gaussian functions
    for i in range(N):
        for j in range(N):
            for k in range(N):
                for l in range(N):
                    R_ap = Exp_He1s[i] * R / (Exp_He1s[i] + Exp_H1s[j])
                    R_bp = R - R_ap
                    R_aq = Exp_He1s[k] * R / (Exp_He1s[k] + Exp_H1s[l])
                    R_bq = R - R_aq
                    R2_ap = R_ap ** 2
                    R2_bp = R_bp ** 2
                    R2_aq = R_aq * R_aq
                    R2_bq = R_bq * R_bq
                    R_pq = R_ap - R_aq
                    R2_pq = R_pq * R_pq

                    V1111 = (
                        V1111
                        + TwoE_int(
                            Exp_H1s[i],
                            Exp_H1s[j],
                            Exp_H1s[k],
                            Exp_H1s[l],
                            0.0,
                            0.0,
                            0.0,
                        )
                        * Coe_H1s[i]
                        * Coe_H1s[j]
                        * Coe_H1s[k]
                        * Coe_H1s[l]
                    )
                    V2111 = (
                        V2111
                        + TwoE_int(
                            Exp_He1s[i],
                            Exp_H1s[j],
                            Exp_H1s[k],
                            Exp_H1s[l],
                            R2,
                            0.0,
                            R2_ap,
                        )
                        * Coe_He1s[i]
                        * Coe_H1s[j]
                        * Coe_H1s[k]
                        * Coe_H1s[l]
                    )
                    V2121 = (
                        V2121
                        + TwoE_int(
                            Exp_He1s[i],
                            Exp_H1s[j],
                            Exp_He1s[k],
                            Exp_H1s[l],
                            R2,
                            R2,
                            R2_pq,
                        )
                        * Coe_He1s[i]
                        * Coe_H1s[j]
                        * Coe_He1s[k]
                        * Coe_H1s[l]
                    )
                    V2211 = (
                        V2211
                        + TwoE_int(
                            Exp_He1s[i],
                            Exp_He1s[j],
                            Exp_H1s[k],
                            Exp_H1s[l],
                            0.0,
                            0.0,
                            R2,
                        )
                        * Coe_He1s[i]
                        * Coe_He1s[j]
                        * Coe_H1s[k]
                        * Coe_H1s[l]
                    )
                    V2221 = (
                        V2221
                        + TwoE_int(
                            Exp_He1s[i],
                            Exp_He1s[j],
                            Exp_He1s[k],
                            Exp_H1s[l],
                            0.0,
                            R2,
                            R2_bq,
                        )
                        * Coe_He1s[i]
                        * Coe_He1s[j]
                        * Coe_He1s[k]
                        * Coe_H1s[l]
                    )
                    V2222 = (
                        V2222
                        + TwoE_int(
                            Exp_He1s[i],
                            Exp_He1s[j],
                            Exp_He1s[k],
                            Exp_He1s[l],
                            0.0,
                            0.0,
                            0.0,
                        )
                        * Coe_He1s[i]
                        * Coe_He1s[j]
                        * Coe_He1s[k]
                        * Coe_He1s[l]
                    )

    return (
        S12,
        T11,
        T12,
        T22,
        V11H,
        V12H,
        V22H,
        V11He,
        V12He,
        V22He,
        V1111,
        V2111,
        V2121,
        V2211,
        V2221,
        V2222,
    )


### Construct the Hamiltonian which is the summation of all integrals, and the overlap matrix
### Since the global variables use several arguments in the construction of AOs, we need to have them all in Hamiltonian


def Collect(
    S12,
    T11,
    T12,
    T22,
    V11H,
    V12H,
    V22H,
    V11He,
    V12He,
    V22He,
    V1111,
    V2111,
    V2121,
    V2211,
    V2221,
    V2222,
):
    """
    This function will compute the core Hamiltonian H, overlap matrix S, and S^-1/2
    Construct the 4-rank tensor of two-electron integrals
    """

    # Construct the core Hamiltonian elements; the Hamiltonian Matrix is declared and initialized outside
    # the function Ham; the same for other matrices
    H = np.zeros((2, 2))
    H[0, 0] = T11 + V11H + V11He
    H[0, 1] = T12 + V12H + V12He
    H[1, 0] = H[0, 1]
    H[1, 1] = T22 + V22H + V22He

    # Construct the overlap matrix
    S = np.zeros((2, 2))
    S[0, 0] = 1
    S[0, 1] = S12
    S[1, 0] = S12
    S[1, 1] = 1

    # Construct S^-/2 using Canonical Orthogonalization
    X = np.zeros((2, 2))
    X[0, 0] = 1.0 / np.sqrt(2.0 * (1.0 + S12))
    X[0, 1] = X[0, 0]
    X[0, 1] = 1.0 / np.sqrt(2.0 * (1.0 - S12))
    X[1, 1] = -X[0, 1]

    # Convert two-electron integrals to elements of a 4-rank tensor of V(2,2,2,2)
    V = np.zeros((2, 2, 2, 2))
    V[0, 0, 0, 0] = V1111
    V[0, 0, 0, 1] = V2111
    V[0, 0, 1, 0] = V2111
    V[0, 0, 1, 1] = V2211
    V[0, 1, 0, 0] = V2111
    V[0, 1, 0, 1] = V2121
    V[0, 1, 1, 0] = V2121
    V[0, 1, 1, 1] = V2221
    V[1, 0, 0, 0] = V2111
    V[1, 0, 0, 1] = V2121
    V[1, 0, 1, 0] = V2121
    V[1, 0, 1, 1] = V2221
    V[1, 1, 0, 0] = V2211
    V[1, 1, 0, 1] = V2221
    V[1, 1, 1, 0] = V2221
    V[1, 1, 1, 1] = V2222

    return H, S, X, V


############ Implement SCF procedure  ############


def SCF(H, X, Z_H, Z_He, R, V):
    """
    Implement SCF iterations
    """
    Crit = 1e-15  # Convergence threshold
    Maxit = 250  # Maximum number of iteration
    Iter = 0  # Count number of iteration

    ## Step 1: Guess the initial density matrix P ##
    # P is a matrix of zeros, so the Fock matrix F will be the core Hamiltonian only
    P = np.zeros([2, 2])

    while Iter <= Maxit:
        print("  ")
        Iter += 1
        print("Interation number: {:03d}".format(Iter))

        ######### Step 2: Calculate the Fock matrix ######
        ### Calculate two-electron part of the Fock matrix from the density matrix P
        G = np.zeros([2, 2])

        for i in range(2):
            for j in range(2):
                for k in range(2):
                    for l in range(2):
                        G[i, j] += P[k, l] * (V[i, j, k, l] - 0.5 * V[i, l, k, j])

        ### Combine the core Hamiltonian with G to obtain the Fock matrix

        F = H + G

        ### Calculate the electronic energy
        Energy = 0.0
        for i in range(2):
            for j in range(2):
                Energy += 0.5 * P[i, j] * (H[i, j] + F[i, j])

        # Energy2 = 0.0
        # Energy2 += np.sum(0.5*P*(H+F))

        print("Electronic energy = ", Energy)
        # print('Electronic energy calculated py numpy.sum = ', Energy2)

        ####### Step 3: calculate Fprime by using S^-1/2 (X in the code), and S^1/2 (X.T in the code)
        G = np.matmul(F, X)
        Fprime = np.matmul(X.T, G)

        ##### Step 4: Diagonalize the Fock matrix. This will produce Cprime and eigen values E
        # Diagonalization of Fock matrix
        Cprime, E = Diag(Fprime)
        print("                                   ")
        print("Eigen values of the Fock Operators:")
        print(E)
        print("                                   ")
        print("-----------------------------------")
        print("-----------------------------------")

        #### Step 5: Calculate orbital coefficients #######
        C = np.matmul(X, Cprime)

        #### Step 6: Calculate the new density matrix #####
        OldP = np.array(P)
        P = np.zeros((2, 2))
        # Generate new elements of density matrix
        for i in range(2):
            for j in range(2):
                P[i, j] = 0.0
                # Calculate new elements on the basis of new C
                for k in range(1):
                    P[i, j] = P[i, j] + 2.0 * C[i, k] * C[k, j]

        # Check convergence using density matrix
        Delta = P - OldP
        Delta = np.sqrt(np.sum(Delta ** 2) / 4.0)
        if Delta < Crit:
            EnergyTotal = Energy + Z_H * Z_He / R
            print("             ")
            print("Calculation converged")
            print("   ")
            print("Electronic energy =", Energy)
            print("Total energy =", EnergyTotal)
            print("   ")
            print("Happy landing")
            break
        elif Iter >= Maxit:
            print("Not converged")
            break


def Diag(Fprime):
    """
    This function is to diagonalize symmetric matrices using the Jacobi algorithm
    Diagonalization will give the matrix of coefficients Cprime and energy of Orbitals E (eigen values)
    """
    if abs(Fprime[0, 0] - Fprime[1, 1]) > 1.0e-20:
        TheTa = 0.5 * math.atan(2.0 * Fprime[0, 1] / (Fprime[0, 0] - Fprime[1, 1]))
    else:
        TheTa = math.pi / 4.0

    Cprime = np.zeros((2, 2))
    E = np.zeros((2, 2))
    Cprime[0, 0] = math.cos(TheTa)
    Cprime[1, 0] = math.sin(TheTa)
    Cprime[0, 1] = math.sin(TheTa)
    Cprime[1, 1] = -math.cos(TheTa)

    E[0, 0] = (
        Fprime[0, 0] * math.cos(TheTa) ** 2
        + Fprime[1, 1] * math.sin(TheTa) ** 2
        + Fprime[0, 1] * math.sin(2.0 * TheTa)
    )
    E[1, 1] = (
        Fprime[1, 1] * math.cos(TheTa) ** 2
        + Fprime[0, 0] * math.sin(TheTa) ** 2
        + Fprime[0, 1] * math.sin(2.0 * TheTa)
    )
    E[1, 0] = 0.0
    E[0, 1] = 0.0

    # Order eigen values E and eigen vectors Cprime
    if E[1, 1] <= E[0, 0]:
        Temp = E[0, 0]
        E[0, 0] = E[1, 1]
        E[1, 1] = Temp

        Temp = Cprime[0, 0]
        Cprime[0, 0] = Cprime[1, 1]
        Cprime[1, 1] = Temp

    return Cprime, E


##### HF calculation ####


def HFCALC(N, R, Zeta1, Zeta2, Z_H, Z_He):
    """
    Perform the Hartree-Fock calculations
    """
    print("Hartree-Fock calculation uses STO-%dG for H and He" % N)
    (
        S12,
        T11,
        T12,
        T22,
        V11H,
        V12H,
        V22H,
        V11He,
        V12He,
        V22He,
        V1111,
        V2111,
        V2121,
        V2211,
        V2221,
        V2222,
    ) = AO_Integral(N, R, Zeta1, Z_H, Z_H, Z_He)

    H, S, X, V = Collect(
        S12,
        T11,
        T12,
        T22,
        V11H,
        V12H,
        V22H,
        V11He,
        V12He,
        V22He,
        V1111,
        V2111,
        V2121,
        V2211,
        V2221,
        V2222,
    )

    # Do the calculation
    SCF(H, X, Z_H, Z_He, R, V)


# Call the main program
if __name__ == "__main__":
    MAIN()

