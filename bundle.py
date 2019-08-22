# Utility to group together probe hits encountered between a pair of _start, _end probes generated by MONGO_USDT_BLOCK.
# Each pair gets its own thread_local count so that nested pairs can be tracked.
# Hits are sorted by the TID of the thread that was encountered.
class Bundle:
    def __init__(self, start = None):
        # TODO: start/end timers?
        self._probes = [start]
        self._done = False
        if start:
            self.tid = start.tid
            self.name = start.name.replace("_start", "")
            self.count = start.args["count"]
        else:
            self.tid = None
            self.name = None
            self.count = None

    def start(self):
        return self._probes[0]

    def is_start(probe):
        return probe.name.endswith("_start")

    def is_end(self, probe):
        return probe.name.endswith("_end") \
            and probe.args["count"] == self.count

    def has_open_nested_probe(self):
        return isinstance(self._probes[-1], Bundle) and not self._probes[-1]._done

    def push(self, probe):
        if self.has_open_nested_probe():
            self._probes[-1].push(probe)
        elif self.is_end(probe):
            self._done = True
            self._probes.append(probe)
        elif Bundle.is_start(probe):
            self._probes.append(Bundle(probe))
        else:
            self._probes.append(probe)

    def __str__(self):
        out = "{\n"
        out += "num_probes: {}\n".format(len(self._probes))
        out += "tid: {}\n".format(self.tid)
        out += "count: {}\n".format(self.count)
        out += " [\n"
        for probe in self._probes:
            probestr = str(probe)
            for line in probestr.splitlines():
                out += "   " + line + "\n"
        return out + " ]\n}\n"
