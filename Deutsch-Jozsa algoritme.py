from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
import numpy as np
from qiskit.tools.jupyter import *
from qiskit.visualization import *
from ibm_quantum_widgets import *
from qiskit import IBMQ, Aer
from qiskit.providers.ibmq import least_busy
from qiskit import QuantumCircuit, transpile, assemble
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler, Estimator, Session, Options

# Loading your IBM Quantum account(s)
service = QiskitRuntimeService(channel="ibm_quantum")

# Randomly select either a balanced or constant circuit
oracleType = np.random.choice(["b", "c"])
# Specify the number of qubits the oracle uses as input
qubitCount = 4

# Create a quantumregister with the number of qubits specified before, plus one that is used as an output
quantumR = QuantumRegister(qubitCount + 1, 'q')
# Create a classical register to use as output
classicalR = ClassicalRegister(qubitCount, 'c')
# Create a quantum circuit with the two registers
DJ_circ = QuantumCircuit(quantumR, classicalR)

# Example of a balanced oracle
def balancedOracle():
    for i in range(qubitCount):
        DJ_circ.cx(quantumR[i], quantumR[-1])
        
# Example of a constant oracle
def constantOracle():
    pass


DJ_circ.x(quantumR[-1]) # Make the output qubit 1
for i in range(qubitCount+1): # Run hadamard-gates on the whole register
    DJ_circ.h(quantumR[i])
match oracleType: # Add one of the oracles to the circuit
    case "b":
        balancedOracle()
    case "c":
        constantOracle()
for i in range(qubitCount): # Add hadamard-gates to all qubits but the last one, and measure them
    DJ_circ.h(quantumR[i])
    DJ_circ.measure(quantumR[i], classicalR[i])
        
    
aer_sim = Aer.get_backend('aer_simulator') # Select backend
results = aer_sim.run(DJ_circ, shots=1).result() # Run the circuit once 
counts = results.get_counts() # Retrieve the result
'''backend = service.backend('ibm_brisbane')
qc_basic = transpile(DJ_circ, backend)
sampler = Sampler(session=backend, options={"shots":1000}) 
results = sampler.run(qc_basic).result()
counts = results.get_counts() # Retrieve the result'''
if '1' not in list(counts.keys())[0]:
    print("constant")
    print(list(counts.keys())[0])
else:
    print("balanced")
    print(list(counts.keys())[0])
#DJ_circ.draw() # Draw the circuit
plot_histogram(counts)