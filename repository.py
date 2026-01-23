import xarray as xr
import os
import glob


class NetCDFDataHandler:
    def __init__(self, INDIR):
        NETCDF_PATTERN = "air.2m.gauss.*.nc"
        pattern = os.path.join(INDIR, NETCDF_PATTERN)
        self.__files = sorted(glob.glob(pattern))
        self.__dataset = None

    @property
    def dataset(self):
        if self.__dataset is None:
            self.__dataset = xr.open_mfdataset(
                self.__files, chunks="auto", engine="netcdf4"
            )
        return self.__dataset

    def save(self, outputs, outdir):
        for fname, data in outputs.items():
            data.to_netcdf(os.path.join(outdir, fname))

        for fname in outputs:
            INDIR = os.path.join(outdir, fname)
            ds = xr.open_dataset(INDIR, chunks="auto", engine="netcdf4")
            print("\n\ndata saved as : \n\n", ds)

    def clear_outdir(self, outdir):
        for fname in os.listdir(outdir):
            fpath = os.path.join(outdir, fname)
            if os.path.isfile(fpath):
                os.remove(fpath)

    def load_output(self, outdir, file_name):
        file_name = os.path.join(outdir, file_name)
        if not os.path.exists(file_name):
            raise FileNotFoundError(f"File not found: {file_name}")
        return xr.open_dataset(file_name)


class WeatherRepository:
    def __init__(self, INDIR, OUTDIR):
        self.datahandler = NetCDFDataHandler(INDIR)
        self.outdir = OUTDIR

    def read_data(self):
        return self.datahandler.dataset

    def write_data(self, outputs):
        os.makedirs(self.outdir, exist_ok=True)
        self.datahandler.clear_outdir(self.outdir)
        self.datahandler.save(outputs, self.outdir)

    def load_output(self, file_name):
        return self.datahandler.load_output(self.outdir, file_name)
