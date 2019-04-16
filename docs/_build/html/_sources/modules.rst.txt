.. DirectDemod documentation master file, created by
   sphinx-quickstart on Thu May 17 00:16:36 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

DirectDemod: Modules documentation
===================================


Signal object
---------------

.. autoclass:: directdemod.comm.commSignal
   :members:

   .. automethod:: __init__

Specific applications
-----------------------

.. autoclass:: directdemod.decode_noaa.decode_noaa
   :members:

   .. automethod:: __init__

.. autoclass:: directdemod.decode_afsk1200.decode_afsk1200
   :members:

   .. automethod:: __init__

.. autoclass:: directdemod.decode_funcube.decode_funcube
   :members:

   .. automethod:: __init__

.. autoclass:: directdemod.decode_meteorm2.decode_meteorm2
   :members:

   .. automethod:: __init__

Filters
---------------

.. autoclass:: directdemod.filters.filter
   :members:

   .. automethod:: __init__

.. autoclass:: directdemod.filters.rollingAverage
   :members:

   .. automethod:: __init__

.. autoclass:: directdemod.filters.blackmanHarris
   :members:

   .. automethod:: __init__

.. autoclass:: directdemod.filters.hamming
   :members:

   .. automethod:: __init__

.. autoclass:: directdemod.filters.gaussian
   :members:

   .. automethod:: __init__

.. autoclass:: directdemod.filters.butter
   :members:

   .. automethod:: __init__

.. autoclass:: directdemod.filters.remez
   :members:

   .. automethod:: __init__

.. autoclass:: directdemod.filters.blackmanHarrisConv
   :members:

   .. automethod:: __init__

Demodulators
-------------

.. autoclass:: directdemod.demod_fm.demod_fm
   :members:

   .. automethod:: __init__

.. autoclass:: directdemod.demod_am.demod_am
   :members:

.. autoclass:: directdemod.demod_fm.demod_fmAD
   :members:

   .. automethod:: __init__

.. autoclass:: directdemod.demod_am.demod_amFLT
   :members:

   .. automethod:: __init__

Sources
----------

.. autoclass:: directdemod.source.IQwav
   :members:

   .. automethod:: __init__


Sinks
----------

.. autoclass:: directdemod.sink.wavFile
   :members:

   .. automethod:: __init__

.. autoclass:: directdemod.sink.image
   :members:

   .. automethod:: __init__

Chunking helper
---------------

.. autoclass:: directdemod.chunker.chunker
   :members:

   .. automethod:: __init__

Logging
--------

.. autoclass:: directdemod.log.log
   :members:

   .. automethod:: __init__
