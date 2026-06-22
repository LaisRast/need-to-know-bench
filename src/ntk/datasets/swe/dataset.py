from ntk.datasets.manifest import Dataset
from ntk.datasets.swe.system_prompt import SYSTEM_PROMPT
from ntk.datasets.swe.scenarios.repr_01 import scenario as repr_01
from ntk.datasets.swe.scenarios.repr_02 import scenario as repr_02
from ntk.datasets.swe.scenarios.repr_03 import scenario as repr_03
from ntk.datasets.swe.scenarios.verf_01 import scenario as verf_01
from ntk.datasets.swe.scenarios.verf_02 import scenario as verf_02
from ntk.datasets.swe.scenarios.verf_03 import scenario as verf_03
from ntk.datasets.swe.scenarios.hist_01 import scenario as hist_01
from ntk.datasets.swe.scenarios.hist_02 import scenario as hist_02
from ntk.datasets.swe.scenarios.hist_03 import scenario as hist_03
from ntk.datasets.swe.scenarios.exec_01 import scenario as exec_01
from ntk.datasets.swe.scenarios.exec_02 import scenario as exec_02
from ntk.datasets.swe.scenarios.exec_03 import scenario as exec_03
from ntk.datasets.swe.scenarios.caus_01 import scenario as caus_01
from ntk.datasets.swe.scenarios.caus_02 import scenario as caus_02
from ntk.datasets.swe.scenarios.caus_03 import scenario as caus_03
from ntk.datasets.swe.scenarios.tran_01 import scenario as tran_01
from ntk.datasets.swe.scenarios.tran_02 import scenario as tran_02
from ntk.datasets.swe.scenarios.tran_03 import scenario as tran_03
from ntk.datasets.swe.scenarios.aggr_01 import scenario as aggr_01
from ntk.datasets.swe.scenarios.aggr_02 import scenario as aggr_02
from ntk.datasets.swe.scenarios.aggr_03 import scenario as aggr_03

dataset = Dataset(
    name="swe",
    display_name="SWE Dataset",
    version="0.1.0-preview",
    system_prompt=SYSTEM_PROMPT,
    scenarios=[
        repr_01,
        repr_02,
        repr_03,
        verf_01,
        verf_02,
        verf_03,
        hist_01,
        hist_02,
        hist_03,
        exec_01,
        exec_02,
        exec_03,
        caus_01,
        caus_02,
        caus_03,
        tran_01,
        tran_02,
        tran_03,
        aggr_01,
        aggr_02,
        aggr_03,
    ],
)
