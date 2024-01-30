# Importing standard Qiskit libraries
from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
import numpy as np
from qiskit.tools.jupyter import *
from qiskit.visualization import *
from ibm_quantum_widgets import *
from qiskit import IBMQ, Aer
from qiskit.providers.ibmq import least_busy
from qiskit import QuantumCircuit, transpile, assemble
from sympy import Matrix

# qiskit-ibmq-provider has been deprecated.
# Please see the Migration Guides in https://ibm.biz/provider_migration_guide for more detail.
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler, Estimator, Session, Options

def postProcessing(results, secret):
    if len(secret) < len(secret):
        raise Exception ('System will be underdetermined. Minimum ' + str(n) + ' bistrings needed, but only '
                         + str(len(results)) +' returned. Please rerun Simon\'s algorithm.')
    string_list = []

    for key in results:
        if key!= "0"*n:
            string_list.append( [ int(c) for c in key ] )

    print('The result in matrix form is :')
    for a in string_list:
        print (a)

    M=Matrix(string_list).T

    # Construct the agumented matrix
    M_I = Matrix(np.hstack([M,np.eye(M.shape[0],dtype=int)]))
    # Perform row reduction, working modulo 2. We use the iszerofunc property of rref
    # to perform the Gaussian elimination over the finite field.
    M_I_rref = M_I.rref(iszerofunc=lambda x: x % 2==0)
    # In row reduced echelon form, we can end up with a solution outside of the finite field {0,1}.
    # Thus, we need to revert the matrix back to this field by treating fractions as a modular inverse.
    # Since the denominator will always be odd (i.e. 1 mod 2), it can be ignored.

    # Helper function to treat fractions as modular inverse:

    def mod2(x):
        return x.as_numer_denom()[0] % 2

    # Apply our helper function to the matrix
    M_I_final = M_I_rref[0].applyfunc(mod2)

    # Extract the kernel of M from the remaining columns of the last row, when s is nonzero.
    if all(value == 0 for value in M_I_final[-1,:M.shape[1]]):
        result_s="".join(str(c) for c in M_I_final[-1,M.shape[1]:])

    # Otherwise, the sub-matrix will be full rank, so just set s=0...0
    else:
        result_s='0'*M.shape[0]

    # Check whether result_s is equal to initial s:
    print ('Secret string: ' + secret)
    print ('Result string: ' + result_s)
    if (result_s == secret):
        print ('We found the correct answer.')
    else:
        print ('Error. The answer is wrong!')
        

# Loading your IBM Quantum account(s)
service = QiskitRuntimeService(channel="ibm_quantum")

#the length of the encoded secret string, and thus half the number of qubits used in the circuit 
#the secret string encoded in the oracle
secretbitstring = '1101'
controllingbitindex = -1
n = len(secretbitstring)

#the qubit register, the first n-qubits are the qubits that are actually read in the end
inputR = QuantumRegister(n*2, 'q')

classicalR = ClassicalRegister(n, 'c')
simon_circuit = QuantumCircuit(inputR, classicalR)

#apply hadamard gates to all qubits in the first register
for i in range(n):
    simon_circuit.h(inputR[i])
    
#transpose the state of the qubits in the first register to the qubits in the second register
for i in range(n):
    simon_circuit.cx(inputR[i], inputR[i+n])
    
#apply a cnot gate from one of the qubits that's 1 in the secret string in the first register, 
#to all the qubits that are 1 in the secret string in the second register
for i in range(n):
    if secretbitstring[::-1][i] == '1':
        if controllingbitindex != -1:
            simon_circuit.cx(inputR[controllingbitindex], inputR[i+n])
        else:
            controllingbitindex = i
            simon_circuit.cx(inputR[i], inputR[i+n])
            
#apply hadamard gates to all the qubits in the first register            
for i in range(n):
    simon_circuit.h(inputR[i])
    
#measure the qubits
for i in range(n):
    simon_circuit.measure(inputR[i], classicalR[i])
    

shots = n+4
aer_sim = Aer.get_backend('aer_simulator') # Select backend
results = aer_sim.run((simon_circuit), shots=shots).result() # Run the circuit once 
counts = results.get_counts() # Retrieve the result
#backend = service.backend('ibm_brisbane')
#aer_sim = Aer.get_backend('aer_simulator')
#qc_basic = transpile(simon_circuit, backend)
#sampler = Sampler(session=backend, options={"shots":1000}) 
#results = sampler.run(qc_basic).result()
#results = aer_sim.run(simon_circuit, shots=shots).result()
#counts = results.get_counts()
resultlist = []

for z in counts:
    #if z not in resultlist and len(resultlist) < (shots) and int(z) != 0:
    resultlist.append(z)

postProcessing(resultlist, secretbitstring)
plot_histogram(counts)
#simon_circuit.draw()