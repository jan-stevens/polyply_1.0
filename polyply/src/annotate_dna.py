# Copyright 2020 University of Groningen
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from .processor import Processor
import networkx as nx
import numpy as np

class AnnotateDNA(Processor):
    """
    """

    def __init__(self, topology, strands):
        """
        """
        self.topology = topology
        self.strand_idx = strands

    def _combine_complementary_strands(self, meta_molecule, mol_idx):
        if mol_idx in self.strand_idx:
            nbases = len(meta_molecule.nodes)

            # Loop over half the meta_mol
            for ndx in range(nbases):
                current_mol = meta_molecule.nodes[ndx]
                if ndx < nbases // 2:
                    # Define forward and backward base that need to be grouped
                    fbase = current_mol
                    bbase = meta_molecule.nodes[nbases - ndx - 1]

                    # Combine their attribute
                    current_mol['bpid'] = ndx
                    current_mol['graph'] = nx.compose(fbase['graph'], bbase['graph'])
                    current_mol['nnodes'] = fbase['nnodes'] + bbase['nnodes']
                    current_mol['nedges'] = fbase['nedges'] + bbase['nedges']
                    current_mol['build'] = fbase['build'] + bbase['build']
                    current_mol['basepair'] = f"{fbase['resname']},{bbase['resname']}"
                    current_mol['density'] = (fbase['density'] + bbase['density']) / 2
                    current_mol['position'] = [0.33 / np.sqrt(3) * (ndx + 1),
                                               0.33 / np.sqrt(3) * (ndx + 1),
                                               0.33 / np.sqrt(3) * (ndx + 1)]

                    del current_mol['resname']
                    del current_mol['resid']
                else:
                    meta_molecule.remove_node(ndx)

    def run_molecule(self, meta_molecule, mol_idx):
        """
        """
        self._combine_complementary_strands(meta_molecule, mol_idx)
        return meta_molecule

    def run_system(self, system):
        """
        Process `system`.
        Parameters
        ----------
        system: vermouth.system.System
            The system to process. Is modified in-place.
        """
        mols = []
        for mol_idx, molecule in enumerate(system.molecules):
            mols.append(self.run_molecule(molecule, mol_idx))
        system.molecules = mols
