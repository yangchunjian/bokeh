import sys
from collections import OrderedDict
from six.moves import cStringIO as StringIO
import pandas as pd
from .. import charts
from .help_messages import *


def get_input(filepath, buffer):
    """Parse received input options. If buffer is not false (=='f') if
    gets input data from input buffer othewise opens file specified in
    sourcefilename,

    Args:
        filepath (str): path to the file to read from to retrieve data
        buffer (str): if == 't' reads data from input buffer
    """
    if buffer != 'f':
        filepath = StringIO(sys.stdin.read())
    elif filepath is None:
        msg = "No Input! Please specify --source_filename or --buffer t"
        raise IOError(msg)

    source = pd.read_csv(filepath)
    return source


def parse_output_config(output):
    """Parse the output specification string and return the related chart
    output attribute.

    Attr:
        output (str): String with the syntax convention specified for the
            cli output option is as follows: <output_type>://<type_arg>
            Valid values:
                output_type: file or server
                type_arg:
                    file_path if output_type is file
                    serve path if output_type is server
    """
    output_type, output_options = output.split('://')

    if output_type == 'file':
        return {'filename': output_options}

    elif output_type == 'server':
        # TODO: check if server configuration is as flexible as with plotting
        #       interface and add support for url/name if so.
        out_opt = output_options.split("@")
        attrnames = ['server', 'url', 'name']

        # unpack server output parametrs in order to pass them to the plot
        # creation function
        kws = dict((attrn, val) for attrn, val in zip( attrnames, out_opt))
        return {'server': kws['server']}

    else:
        msg = "Unknown output type %s found. Please use: file|server"
        print (msg % output_type)
        return {}


def get_chart_params(title, output):
    """Parse output type and output options and return related chart
    parameters. For example: returns filename if output_type is file
    or server it output_type is server

    Args:
        title (str): the title of your plot.
        output (str): selected output. Follows the following convention:
            <output_type>://<type_arg> where output_type can be
            `file` (in that case type_arg specifies the file path) or
            `server` (in that case type_arg specify the server name).

    """
    params = {'title': title}
    output_params = parse_output_config(output)
    if output_params:
        params.update(output_params)

    return params


def get_data_series(series, source, index):
    """Generate an OrderedDict from the source series excluding index
    and all series not specified in series.

    Args:
        series (list(str)): list of strings specifying the names of the
            series to keep from source
        source (DataFrame): pandas DataFrame with the data series to be
            plotted
        index (str): name of the series of source to be used as index.
    """
    series = define_series(series, source, index)
    # generate charts data
    data_series = OrderedDict()
    for i, colname in enumerate(series+[index]):
        try:
            data_series[colname] = source[colname]
        except KeyError:
            raise KeyError(ERR_MSG_SERIES_NOT_FOUND % (colname, source.keys()))

    return data_series


def define_series(series, source, index):
    """If series is empty returns source_columns excluding the column
    where column == index. Otherwise returns the series.split(',')

    Args:
        series (str): string that contains the names of the
            series to keep from source, separated by `,`
        source (DataFrame): pandas DataFrame with the data series to be
            plotted
        index (str): name of the series of source to be used as index.
    """
    if not series:
        return [c for c in source.columns if c != index]
    else:
        return series.split(',')


def get_charts_mapping():
    """Return a dict with chart classes names (lower case) as keys and
    their related class as values.
    """
    mapping = {}
    for (clsname, cls) in charts.__dict__.items():
        try:
            if issubclass(cls, charts.ChartObject):
                mapping[clsname.lower()] = cls
        except TypeError:
            pass
    return mapping