# Create an AliceBobQPU class accepting myQLM jobs and returning a myQLM result

from qat.core import Result
from qat.core.qpu import QPUHandler
from qat.interop.qiskit import qlm_to_qiskit
from qiskit_alice_bob_provider import AliceBobRemoteProvider, AliceBobLocalProvider
from qiskit import transpile

class AliceBobQPU(QPUHandler):
    def __init__(self, backend_name, average_nb_photons=None, local=True):
        super().__init__()  # Please ensure parents constructor is called
        self.backend_name = backend_name
        self.local = local
        self.average_nb_photons = average_nb_photons

    def submit_job(self, job):
        qiskit_circuit = qlm_to_qiskit(job.circuit)

        if self.local:
          provider = AliceBobLocalProvider()
        else:
          provider = AliceBobRemoteProvider(api_key = 'YOUR_API_KEY_HERE')

        if self.average_nb_photons is not None:
          backend = provider.get_backend(self.backend_name, average_nb_photons=self.average_nb_photons)
        else:
           backend = provider.get_backend(self.backend_name)
        qiskit_circuit = transpile(qiskit_circuit, backend)
        qiskit_job = backend.run(qiskit_circuit, shots=job.nbshots)

        qiskit_counts = qiskit_job.result().get_counts()

        myqlm_result = Result(lsb_first=True, nbqbits=job.circuit.nbqbits)

        for s, p in qiskit_counts.items():
          myqlm_result.add_sample(state=int(s,2), probability=p/job.nbshots)

        myqlm_result.meta_data = {'nbshots': job.nbshots}

        return myqlm_result