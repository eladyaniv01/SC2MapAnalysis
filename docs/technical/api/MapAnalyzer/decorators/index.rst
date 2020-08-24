:orphan:

:mod:`MapAnalyzer.decorators`
=============================

.. py:module:: MapAnalyzer.decorators


Module Contents
---------------


Functions
~~~~~~~~~

.. autoapisummary::

   MapAnalyzer.decorators.provide_progress_bar
   MapAnalyzer.decorators.progress_wrapped


.. function:: provide_progress_bar(function: Callable, estimated_time: int, tstep: float = 0.2, tqdm_kwargs: Optional[Dict[str, str]] = None, args: Optional[Tuple['MapData']] = None, kwargs: Optional[Dict[Any, Any]] = None) -> None

   Tqdm wrapper for a long-running function
   :param function - function to run:
   :param estimated_time - how long you expect the function to take:
   :param tstep - time delta:
   :type tstep - time delta: seconds
   :param tqdm_kwargs - kwargs to construct the progress bar:
   :param args - args to pass to the function:
   :param kwargs - keyword args to pass to the function:

   ret:
       function(*args, **kwargs)


.. function:: progress_wrapped(estimated_time: int, desc: str = 'Progress', tstep: float = 0.2, tqdm_kwargs: None = None) -> Callable

   Decorate a function to add a progress bar


