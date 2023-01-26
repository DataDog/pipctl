🐍 pipctl 🤗
------------

To make things clear from the beginning - this tool, ``pipctl``, is pronounced as "*pip cuddle*". 🤗🐍

**Notice:** This tool is just a prototype.

The tool provides the ability to generate a requirements file with all the dependencies locked (similarly as `pip-tools <https://pypi.org/project/pip-tools/>`__ does) but stating dependencies without vulnerabilities or only with the acceptable ones. `OSV <https://osv.dev>`_ database is used as a source of known vulnerabilities.

Usage
=====

First, install the tool:

.. code-block:: console

  pip install pipctl

Create a configuration file:

.. code-block:: console

  pipctl config

An example content of ``pipctl.yaml``:

.. code-block:: yaml

  # A listing of vulnerabilities that are acceptable in the application. OSV.dev is used as a source.
  acceptable_vulnerabilities: []
  # A path to requirements.txt file, relative to this configuration file.
  requirements_file: ./requirements.txt

State your dependencies in ``requirements.txt`` (or ``requirements.in`` as in case of `pip-tools <https://pypi.org/project/pip-tools/>`__; the file name is stated in the configuration file):

.. code-block:: text

  flask<=2.2.2

To generate a requirements file, run the following command:

.. code-block:: console

  pipctl constraint > requirements-pipctl.txt

An example output produced (content of ``requirements-pipctl.txt``):

.. code-block:: console

  click==8.1.3
  flask==2.2.2
  importlib-metadata==6.0.0
  itsdangerous==2.1.2
  jinja2==3.1.2
  markupsafe==2.1.1
  werkzeug==2.2.2
  zipp==3.11.0

Subsequently, the application requirements can be installed using ``pip``:

.. code-block:: console

  pip install -r requirements-pipctl.txt

If you use another formats to store requirements, consider using `micropipenv <https://github.com/thoth-station/micropipenv>`_ and its ``micropipenv requirements`` subcommand to perform translation.

If the resolution using ``pipctl`` fails because of vulnerabilities present, check exploitability of dependencies present (based on messages printed to stderr). If vulnerabilities are acceptable, state them in ``pipctl.yaml`` file and rerun the resolution process.

Example:

.. code-block:: console

  $ cat pipctl.yaml
  acceptable_vulnerabilities: []
  requirements_file: ./requirements.txt

  $ cat requirements.txt
  urllib3==1.26.0

  $ pipctl constraint
   WARNING: Adding constraint 'urllib3!=1.26.0' based on vulnerability GHSA-5phf-pp7p-vc2r - see https://osv.dev/vulnerability/GHSA-5phf-pp7p-vc2r
   ERROR: Cannot install urllib3!=1.26.0 and urllib3==1.26.0 because these package versions have conflicting dependencies.
   ERROR: Traceback (most recent call last):
     File "/Users/fridolin.pokorny/git/fridex/pipctl/venv/lib/python3.9/site-packages/pip/_vendor/resolvelib/resolvers.py", line 348, in resolve
       self._add_to_criteria(self.state.criteria, r, parent=None)
     File "/Users/fridolin.pokorny/git/fridex/pipctl/venv/lib/python3.9/site-packages/pip/_vendor/resolvelib/resolvers.py", line 173, in _add_to_criteria
       raise RequirementsConflicted(criterion)
   pip._vendor.resolvelib.resolvers.RequirementsConflicted: Requirements conflict: SpecifierRequirement('urllib3==1.26.0'), SpecifierRequirement('urllib3!=1.26.0')
  ...

An updated configuration file stating acceptable vulnerabilities `GHSA-5phf-pp7p-vc2r <https://osv.dev/vulnerability/GHSA-5phf-pp7p-vc2r>`_ and `GHSA-q2q7-5pp4-w6pg <https://osv.dev/vulnerability/GHSA-q2q7-5pp4-w6pg>`_ leading to a successful resolution:

.. code-block:: yaml

  $ cat pipctl.yaml  # A new pipctl.yaml file
  acceptable_vulnerabilities: [GHSA-5phf-pp7p-vc2r, GHSA-q2q7-5pp4-w6pg]
  requirements_file: ./requirements.txt

  $ cat requirements.txt
  urllib3==1.26.0

  $ pipctl constraint
  2023-01-11 18:12:34,240 [79773] INFO     pipctl._osv: Downloading OSV database
  WARNING: Ignoring vulnerability 'GHSA-5phf-pp7p-vc2r'
  WARNING: Ignoring vulnerability 'GHSA-q2q7-5pp4-w6pg'
  WARNING: Ignoring vulnerability 'PYSEC-2021-108'
  WARNING: Ignoring vulnerability 'PYSEC-2021-59'
  urllib3==1.26.0

Another example of a resolution finding a set of dependencies without vulnerability:

.. code-block:: yaml

  $ cat requirements.in                                  
  flask<2
  certifi<=2022.9.24
  
  $ cat pipctl.yaml 
  acceptable_vulnerabilities: []
  requirements_file: ./requirements.in
  
  $ python3 ./pipctl-cli constraints
  2022-12-19 10:16:44,087 [92142] INFO     pipctl._osv: Downloading OSV database
  WARNING: Adding constraint 'certifi!=2022.9.24' based on vulnerability GHSA-43fp-rhv2-5gv8 - see https://osv.dev/vulnerability/GHSA-43fp-rhv2-5gv8
  WARNING: Adding constraint 'werkzeug!=1.0.1' based on vulnerability PYSEC-2022-203 - see https://osv.dev/vulnerability/PYSEC-2022-203
  WARNING: Adding constraint 'certifi!=2022.9.14' based on vulnerability GHSA-43fp-rhv2-5gv8 - see https://osv.dev/vulnerability/GHSA-43fp-rhv2-5gv8
  WARNING: Adding constraint 'certifi!=2022.6.15.2' based on vulnerability GHSA-43fp-rhv2-5gv8 - see https://osv.dev/vulnerability/GHSA-43fp-rhv2-5gv8
  WARNING: Adding constraint 'certifi!=2022.6.15.1' based on vulnerability GHSA-43fp-rhv2-5gv8 - see https://osv.dev/vulnerability/GHSA-43fp-rhv2-5gv8
  WARNING: Adding constraint 'certifi!=2022.6.15' based on vulnerability GHSA-43fp-rhv2-5gv8 - see https://osv.dev/vulnerability/GHSA-43fp-rhv2-5gv8
  WARNING: Adding constraint 'certifi!=2022.5.18.1' based on vulnerability GHSA-43fp-rhv2-5gv8 - see https://osv.dev/vulnerability/GHSA-43fp-rhv2-5gv8
  WARNING: Adding constraint 'werkzeug!=1.0.0' based on vulnerability PYSEC-2022-203 - see https://osv.dev/vulnerability/PYSEC-2022-203
  WARNING: Adding constraint 'certifi!=2021.10.8' based on vulnerability GHSA-43fp-rhv2-5gv8 - see https://osv.dev/vulnerability/GHSA-43fp-rhv2-5gv8
  WARNING: Adding constraint 'werkzeug!=0.16.1' based on vulnerability PYSEC-2022-203 - see https://osv.dev/vulnerability/PYSEC-2022-203
  WARNING: Adding constraint 'certifi!=2021.5.30' based on vulnerability GHSA-43fp-rhv2-5gv8 - see https://osv.dev/vulnerability/GHSA-43fp-rhv2-5gv8
  WARNING: Adding constraint 'certifi!=2020.12.5' based on vulnerability GHSA-43fp-rhv2-5gv8 - see https://osv.dev/vulnerability/GHSA-43fp-rhv2-5gv8
  WARNING: Adding constraint 'werkzeug!=0.16.0' based on vulnerability PYSEC-2022-203 - see https://osv.dev/vulnerability/PYSEC-2022-203
  WARNING: Adding constraint 'werkzeug!=0.15.6' based on vulnerability PYSEC-2022-203 - see https://osv.dev/vulnerability/PYSEC-2022-203
  WARNING: Adding constraint 'werkzeug!=0.15.5' based on vulnerability PYSEC-2022-203 - see https://osv.dev/vulnerability/PYSEC-2022-203
  WARNING: Adding constraint 'werkzeug!=0.15.4' based on vulnerability PYSEC-2022-203 - see https://osv.dev/vulnerability/PYSEC-2022-203
  WARNING: Adding constraint 'werkzeug!=0.15.3' based on vulnerability PYSEC-2022-203 - see https://osv.dev/vulnerability/PYSEC-2022-203
  WARNING: Adding constraint 'certifi!=2020.11.8' based on vulnerability GHSA-43fp-rhv2-5gv8 - see https://osv.dev/vulnerability/GHSA-43fp-rhv2-5gv8
  WARNING: Adding constraint 'certifi!=2020.6.20' based on vulnerability GHSA-43fp-rhv2-5gv8 - see https://osv.dev/vulnerability/GHSA-43fp-rhv2-5gv8
  WARNING: Adding constraint 'certifi!=2020.4.5.2' based on vulnerability GHSA-43fp-rhv2-5gv8 - see https://osv.dev/vulnerability/GHSA-43fp-rhv2-5gv8
  WARNING: Adding constraint 'certifi!=2020.4.5.1' based on vulnerability GHSA-43fp-rhv2-5gv8 - see https://osv.dev/vulnerability/GHSA-43fp-rhv2-5gv8
  WARNING: Adding constraint 'werkzeug!=0.15.2' based on vulnerability GHSA-gq9m-qvpx-68hc - see https://osv.dev/vulnerability/GHSA-gq9m-qvpx-68hc
  WARNING: Adding constraint 'werkzeug!=0.15.1' based on vulnerability GHSA-gq9m-qvpx-68hc - see https://osv.dev/vulnerability/GHSA-gq9m-qvpx-68hc
  WARNING: Adding constraint 'certifi!=2020.4.5' based on vulnerability GHSA-43fp-rhv2-5gv8 - see https://osv.dev/vulnerability/GHSA-43fp-rhv2-5gv8
  WARNING: Adding constraint 'werkzeug!=0.15.0' based on vulnerability GHSA-gq9m-qvpx-68hc - see https://osv.dev/vulnerability/GHSA-gq9m-qvpx-68hc
  WARNING: Adding constraint 'certifi!=2019.11.28' based on vulnerability GHSA-43fp-rhv2-5gv8 - see https://osv.dev/vulnerability/GHSA-43fp-rhv2-5gv8
  WARNING: Adding constraint 'certifi!=2019.9.11' based on vulnerability GHSA-43fp-rhv2-5gv8 - see https://osv.dev/vulnerability/GHSA-43fp-rhv2-5gv8
  WARNING: Adding constraint 'certifi!=2019.6.16' based on vulnerability GHSA-43fp-rhv2-5gv8 - see https://osv.dev/vulnerability/GHSA-43fp-rhv2-5gv8
  WARNING: Adding constraint 'certifi!=2019.3.9' based on vulnerability GHSA-43fp-rhv2-5gv8 - see https://osv.dev/vulnerability/GHSA-43fp-rhv2-5gv8
  WARNING: Adding constraint 'certifi!=2018.11.29' based on vulnerability GHSA-43fp-rhv2-5gv8 - see https://osv.dev/vulnerability/GHSA-43fp-rhv2-5gv8
  WARNING: Adding constraint 'certifi!=2018.10.15' based on vulnerability GHSA-43fp-rhv2-5gv8 - see https://osv.dev/vulnerability/GHSA-43fp-rhv2-5gv8
  WARNING: Adding constraint 'certifi!=2018.8.24' based on vulnerability GHSA-43fp-rhv2-5gv8 - see https://osv.dev/vulnerability/GHSA-43fp-rhv2-5gv8
  WARNING: Adding constraint 'certifi!=2018.8.13' based on vulnerability GHSA-43fp-rhv2-5gv8 - see https://osv.dev/vulnerability/GHSA-43fp-rhv2-5gv8
  WARNING: Adding constraint 'certifi!=2018.4.16' based on vulnerability GHSA-43fp-rhv2-5gv8 - see https://osv.dev/vulnerability/GHSA-43fp-rhv2-5gv8
  WARNING: Adding constraint 'certifi!=2018.1.18' based on vulnerability GHSA-43fp-rhv2-5gv8 - see https://osv.dev/vulnerability/GHSA-43fp-rhv2-5gv8
  WARNING: Adding constraint 'certifi!=2017.11.5' based on vulnerability GHSA-43fp-rhv2-5gv8 - see https://osv.dev/vulnerability/GHSA-43fp-rhv2-5gv8
  certifi==2017.7.27.1
  click==8.1.3
  flask==1.1.2
  itsdangerous==2.1.2
  jinja2==3.1.2
  markupsafe==2.1.1
  werkzeug==2.2.2

Configuration file
==================

The configuration file can be generated using:

.. code-block:: console

  pipctl config

An example configuration file can look like this:

.. code-block:: yaml

  # A listing of vulnerabilities that are acceptable in the application. OSV.dev is used as a source.
  acceptable_vulnerabilities:
  - GHSA-5wv5-4vpf-pj6m   # See https://osv.dev/vulnerability/GHSA-5wv5-4vpf-pj6m
  requirements_file: ./requirements.txt

Each vulnerability can be referenced using its identifier or one of its aliases stated in the `OSV.dev <https://osv.dev>`_ database, see examples listed above.

License
=======

See the LICENSE file.
