class Stats:
    def __init__(self, env, base_stations, clients, area, slices):
        # self.per_slice_cac = dict()
        self.env = env
        self.base_stations = base_stations
        self.clients = clients
        self.area = area
        self.slices = slices
        #self.graph = graph

        # Stats
        self.total_connected_users_ratio = []
        self.total_used_bw = []
        self.avg_slice_load_ratio = []
        self.avg_slice_client_count = []
        self.coverage_ratio = []
        self.connect_attempt = []
        self.block_count = []
        self.handover_count = []
        self.per_slice_load_ratio = []
        self.per_slice_load = []
        self.per_slice_client_count = []
        self.per_slice_cac_rate = []

    def get_stats(self):
        # print((
        #     self.total_connected_users_ratio,
        #     self.total_used_bw,
        #     self.avg_slice_load_ratio,
        #     self.avg_slice_client_count,
        #     self.coverage_ratio,
        #     self.block_count,
        #     self.handover_count,
        #     self.per_slice_load_ratio,
        #     self.per_slice_load,
        #     self.per_slice_client_count
        # ))
        return (
            self.total_connected_users_ratio,
            self.total_used_bw,
            self.avg_slice_load_ratio,
            self.avg_slice_client_count,
            self.coverage_ratio,
            self.block_count,
            self.handover_count,
        )

    def get_per_slice_stats(self):
        return {'per_slice_load_ratio': self.per_slice_load_ratio,
                'per_slice_load': self.per_slice_load,
                'per_slice_client_count': self.per_slice_client_count,
                'per_slice_cac': self.per_slice_cac_rate}

    def collect(self):
        yield self.env.timeout(0.25)
        self.connect_attempt.append(0)
        self.block_count.append(0)
        self.handover_count.append(0)
        while True:
            self.block_count[-1] /= self.connect_attempt[-1] if self.connect_attempt[-1] != 0 else 1
            self.handover_count[-1] /= self.connect_attempt[-1] if self.connect_attempt[-1] != 0 else 1

            self.total_connected_users_ratio.append(self.get_total_connected_users_ratio())
            self.total_used_bw.append(self.get_total_used_bw())
            self.avg_slice_load_ratio.append(self.get_avg_slice_load_ratio())
            self.avg_slice_client_count.append(self.get_avg_slice_client_count())
            self.coverage_ratio.append(self.get_coverage_ratio())

            self.per_slice_load_ratio.append(self.get_per_slice_load_ratio())
            self.per_slice_load.append(self.get_per_slice_load())
            self.per_slice_client_count.append(self.get_per_slice_client_count())
            self.per_slice_cac_rate.append(self.get_per_slice_cac())

            self.connect_attempt.append(0)
            self.block_count.append(0)
            self.handover_count.append(0)
            # !!!!!!!!!!
            self.clear_slice_cac()
            yield self.env.timeout(1)

    def get_total_connected_users_ratio(self):
        t, cc = 0, 0
        for c in self.clients:
            if self.is_client_in_coverage(c):
                t += c.connected
                cc += 1
        # for bs in self.base_stations:
        #     for sl in bs.slices:
        #         t += sl.connected_users
        return t/cc if cc != 0 else 0

    def get_total_used_bw(self):
        t = 0
        for bs in self.base_stations:
            for sl in bs.slices:
                t += sl.capacity.capacity - sl.capacity.level
        return t

    def get_avg_slice_load_ratio(self):
        t, c = 0, 0
        for bs in self.base_stations:
            for sl in bs.slices:
                c += sl.capacity.capacity
                t += sl.capacity.capacity - sl.capacity.level
                #c += 1
                #t += (sl.capacity.capacity - sl.capacity.level) / sl.capacity.capacity
        return t/c if c != 0 else 0

    def get_per_slice_load_ratio(self):
        """
        Method returns slice load expressed as used slice bandwidth over slice capacity
        :return:
        """
        _slices = dict()
        for bs in self.base_stations:
            for sl in bs.slices:
                try:
                    _slices[sl.name].update({
                        'capacity': (_slices[sl.name]['capacity'] + sl.capacity.capacity) / 2,
                        'used_capacity': (_slices[sl.name]['used_capacity'] + (
                                    sl.capacity.capacity - sl.capacity.level)) / 2
                    })
                except KeyError:
                    _slices.update({sl.name: {
                        'capacity': sl.capacity.capacity,
                        'used_capacity': sl.capacity.capacity - sl.capacity.level
                    }})
        return _slices

    def get_per_slice_cac(self):
        """
        Method returns slice ue cac
        :return:
        """
        _slices = dict()
        for bs in self.base_stations:
            for sl in bs.slices:
                print(sl.ue_cac)
                try:
                    _slices[sl.name].update({
                        'ue_cac': (_slices[sl.name]['ue_cac'] + sl.ue_cac)
                    })
                except KeyError:
                    _slices.update({sl.name: {'ue_cac': sl.ue_cac}})

        return _slices

    def get_per_slice_load(self):
        """
        Method returns total used BW in a given slice
        :return:
        """
        _slices = dict()
        for bs in self.base_stations:
            for sl in bs.slices:
                try:
                    _slices[sl.name].update({
                        'used_capacity': _slices[sl.name]['used_capacity'] + sl.capacity.capacity
                    })
                except KeyError:
                    _slices.update({sl.name: {
                        'used_capacity': sl.capacity.capacity
                    }})
        return _slices

    def get_avg_slice_client_count(self):
        t, c = 0, 0
        _slices = []
        for bs in self.base_stations:
            for sl in bs.slices:
                if sl.name not in _slices:
                    _slices.append(sl.name)
                t += sl.connected_users
        return t/len(_slices) if len(_slices) !=0 else 0

    def get_per_slice_client_count(self):
        """
        Method returns total client count per slice
        :return:
        """
        _slices = dict()
        for bs in self.base_stations:
            for sl in bs.slices:
                try:
                    _slices[sl.name].update({
                        'client_count': _slices[sl.name]['client_count'] + sl.connected_users
                    })
                except KeyError:
                    _slices.update({sl.name: {
                        'client_count': sl.connected_users
                    }})
        return _slices

    def get_coverage_ratio(self):
        t, cc = 0, 0
        for c in self.clients:
            if self.is_client_in_coverage(c):
                cc += 1
                if c.base_station is not None and c.base_station.coverage.is_in_coverage(c.x, c.y):
                    t += 1
        return t/cc if cc !=0 else 0

    def incr_connect_attempt(self, client):
        if self.is_client_in_coverage(client):
            self.connect_attempt[-1] += 1

    def incr_block_count(self, client):
        if self.is_client_in_coverage(client):
            self.block_count[-1] += 1

    def incr_handover_count(self, client):
        if self.is_client_in_coverage(client):
            self.handover_count[-1] += 1

    def is_client_in_coverage(self, client):
        xs, ys = self.area
        return True if xs[0] <= client.x <= xs[1] and ys[0] <= client.y <= ys[1] else False

    def incr_per_slice_cac(self, client, slice_name):
        if self.is_client_in_coverage(client):
            try:
                self.per_slice_cac[slice_name] += 1
            except KeyError:
                self.per_slice_cac.update({slice_name: 1})

    def clear_slice_cac(self):
        """
        abominacja
        :return:
        """
        for bs in self.base_stations:
            for sl in bs.slices:
                sl.clear_ue_cac()
