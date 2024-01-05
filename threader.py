from threading import Thread

def run_as_thread(function, callback, prefunction=None):

    if prefunction is not None:
        prefunction()

    def _worker():
        result = function()
        callback(result)

    thread = Thread(target=_worker)
    thread.start()