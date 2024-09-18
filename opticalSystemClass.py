import numpy as np
import matplotlib.pyplot as plt

"""
    This module is designed to build matrices for ABCD Optics Matrices for the propagation of a guassian beam through an optical system.
    The optical elements currently supported are:
    - Free Space Propagation
    - Thin/Thick Lens
    - Flat/Curved Mirror
    - Interface between two media
    The module also supports plotting the beam profile after propagation through the optical system.
"""

class OpticalSystem:
    def __init__(self, wavelength, waist, z=0, theta=0, R=np.inf):
        """
            Initialize the Beam Parameters
        """
        #one_over_q = 1/R - 1j*np.pi*waist**2/wavelength
        self.q = 1j*np.pi*waist**2/wavelength
        self.wavelength = wavelength
        self.waist = waist
        self.theta = theta
        #self.z_0 = z
        self.z = z
        self.optics = []

    def freeSpace(self, d, add = True):
        """
        This function returns the ABCD matrix for free space propagation
        """
        #self.z = self.z + d
        if add == True:
            self.optics.append(np.matrix([[1, d], [0, 1]]))
        else:
            return np.matrix([[1, d], [0, 1]])

    def lens(self, f, n1=0, n2=0, d=0, type='thin'):
        """
        This function returns the ABCD matrix for a lens
        """
        #self.z = 0
        #self.z_0 = f
        if type == 'thin':
            self.optics.append(np.matrix([[1, 0], [-1/f, 1]]))
        elif type == 'thick':
            self.optics.append(np.matrix([[1, 0], [(n2-n1)/n1/f, n2/n1]]) @ self.freeSpace(d,add=False) @ np.matrix([[1, 0], [(n1-n2)/n2/f, n1/n2]]))
        else:
            raise ValueError('Invalid lens type')

    def mirror(self, radius=0, type='flat'):
        """
        This function returns the ABCD matrix for a mirror
        """
        if type == 'flat':
            self.optics.append(np.matrix([[1, 0], [0, 1]]))
        elif type == 'curved':
            self.optics.append(np.matrix([[1, 0], [-2/radius, 1]]))
        else:
            raise ValueError('Invalid mirror type')

    def interface(self, n1, n2, d):
        """
        This function returns the ABCD matrix for an interface
        """
        initialInt = np.matrix([[1, 0], [0, n1/n2]])
        propagation = self.freeSpace(d,add=False)
        finalInt = np.matrix([[1, 0], [0, n2/n1]])
        self.optics.append(initialInt @ propagation @ finalInt)
        
    def plotOpticalSystem(self):
        """
            This function plots the optics that have been added to the optics list.
            I don't know how to do this in a pretty way yet, but it could be cool.
            Definitely just for fun if someone wants to try it.
        """
        pass

    def propagate_beam(self):
        """
        This function propagates a Gaussian beam through an optical system using ABCD matrices and returns the results as a dictionary.
        """
        beamMatrix = np.matrix([[self.z], [self.theta]])
        qMatrix = np.matrix([[self.q], [1]])
        ABCD_matrix = np.eye(2)
        for element in reversed(self.optics):
            ABCD_matrix = np.matmul(ABCD_matrix, element)
        beamMatrix = np.matmul(ABCD_matrix, beamMatrix)
        A = ABCD_matrix[0, 0]; B = ABCD_matrix[0, 1]; C = ABCD_matrix[1, 0]; D = ABCD_matrix[1, 1]
        self.q_out = A*self.q + B/(C*self.q + D)
        """
            Use this with some amount of caution. I am not sure how to include the real component of the q parameter in the calculation.
            The imaginary component is used to determine the Rayleigh range of the beam while the real compenent is related to the position of the beam along the axis of propagation.
            This means that as the real componenet of the beam changes (gets further from the minimum waist position), the beam will diverge.
            The way that the code below is supposed to work is that it calculates the minimum waist of the beam based on the rayleigh range and then scales it based on the,
            position of the beam along the z-axis. If this is incorrect, please let me know.
        """
        self.waist_out = np.sqrt(self.wavelength * np.abs(np.imag(self.q_out)) / np.pi) * np.sqrt(1 + (np.real(self.q_out) / np.imag(self.q_out))**2)
        self.z_out = beamMatrix[0, 0]
        self.theta_out = beamMatrix[1, 0]

    def plotBeamProfile(self):
        """
            These plots currently only make sense if you are imaging the beam at the most collimated portion of the beam (ie. when the radius of curvature is infinity).
            Currently it won't tell you where you are along the z-axis because I have not properly implemented that.
        """
        if hasattr(self, 'waist_out'):
            z1_values = np.linspace(-10*self.waist_out, 10*self.waist_out, 100)
            beam_profile = np.exp(-z1_values**2/(self.waist_out**2))

            z_r = np.pi*self.waist_out**2/self.wavelength
            z2_values = np.linspace(-2*z_r, 2*z_r, 100)
            w_z = self.waist_out*np.sqrt(1 + (z2_values/z_r)**2)
            w_z2 = np.sqrt(2)*self.waist_out

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

            ax1.plot(z1_values, beam_profile)
            ax1.set_xlabel('Position (z)')
            ax1.set_ylabel('Intensity')
            ax1.set_title(f"Gaussian Beam Profile at Waist: {self.waist_out*1e6} um")

            ax2.plot(z2_values, w_z, color='red')
            ax2.plot(z2_values, -w_z, color='red')  # Add a mirror image of the beam waist
            ax2.axvline(x=0, color='blue', linestyle='--', label='waist_out', ymin=.5,ymax=.5+self.waist_out/w_z.max()/2)
            ax2.axvline(x=z_r, color='green', linestyle='--', label='sqrt(2)*waist_out', ymin=.5, ymax=.5+w_z2/w_z.max()/2)
            ax2.set_xlabel('Position (z)')
            ax2.set_ylabel('Beam Waist')
            ax2.yaxis.set_label_position("right")
            ax2.yaxis.tick_right()
            ax2.set_title(f"Gaussian Beam Waist vs. Position")
            ax2.legend()

            plt.show()
        else:
            raise ValueError('Beam has not been propagated yet. Run the propagate_beam() method first.')
