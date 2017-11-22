#  plot.py
#  by Behnam Heydarshahi, November 2017
#  This module draws charts
import matplotlib
import numpy

# matplotlib.use('Agg')
import matplotlib.pyplot as plt
import datetime
import time

# This should be set by server:
# os.environ["DISPLAY"] = "localhost:16.0"

from model import constants

CAPSIZE = 4
PLOT_START = 0
PLOT_END = 1




def plot_accuracies(l_title, l_axis_x, l_axis_y, l1, x1, y1, l2, x2, y2):
    plt.plot(x1, y1, color='r', label=l1)
    plt.plot(x1, y1, 'ro')

    plt.plot(x2, y2, color='b', label=l2)
    plt.plot(x2, y2, 'bs')

    plt.title(l_title)
    plt.xlabel(l_axis_x)
    plt.ylabel(l_axis_y)

    plt.axis([0, 100, 0, 100])
    plt.legend(loc='best')
    plt.show(block=False)
    plt.savefig('./part1_accuracies.png')



def plot_accuracies_with_stderr(l_title, l_axis_x, l_axis_y, l1, x1, y1, y1err, l2, x2, y2, y2err,
                                l3, x3, y3, y3err, l4, x4, y4, y4err):

    plt.errorbar(x1,  y1, yerr=y1err, color='r', label=l1, capsize=CAPSIZE)
    plt.plot(x1, y1, 'ro')

    plt.errorbar(x2,  y2, yerr=y2err, color='b', label=l2, capsize=CAPSIZE)
    plt.plot(x2, y2, 'bo')

    plt.errorbar(x3,  y3, yerr=y3err, color='g', label=l3, capsize=CAPSIZE)
    plt.plot(x3, y3, 'gs')

    plt.errorbar(x4,  y4, yerr=y4err, color='y', label=l4, capsize=CAPSIZE)
    plt.plot(x4, y4, 'ys')

    plt.title(l_title)
    plt.xlabel(l_axis_x)
    plt.ylabel(l_axis_y)

    plt.axis([0, 550, 0, 100])
    plt.legend(loc='best')
    plt.show(block=False)
    plt.savefig('./output/hw1_part_2_accuracies_with_stderr.png')


#plotables
#l1_list, x1_list, y1_list, y1err_list

# Credits: https://stackoverflow.com/questions/14720331/how-to-generate-random-colors-in-matplotlib
def get_cmap(n, name='hsv'):
    '''Returns a function that maps each index in 0, 1, ..., n-1 to a distinct
    RGB color; the keyword argument name must be a standard mpl colormap name.'''
    return plt.cm.get_cmap(name, n)


def plot_y_with_stderr(main_title, x_axis_tile, y_axis_title, range_x, range_y, subplotables,
                       output_file_name):
    cmap = get_cmap(len(subplotables) + 1)

    for i, plotable in enumerate(subplotables):
        color = cmap(i)
        if constants.DEBUG_VERBOSE:
            print " color {} = {}".format(i, color)

        # Values and errors
        plt.errorbar(plotable.x_values, plotable.y_values, plotable.y_std_err_values, color=color,
                     label=plotable.label, capsize=CAPSIZE)

        # the dots
        # plt.plot(plotable.x_values, plotable.y_values, )

    plt.title(main_title)
    plt.xlabel(x_axis_tile)
    plt.ylabel(y_axis_title)
    if range_x is not None:
        plt.axis([range_x[PLOT_START], range_x[PLOT_END], range_y[PLOT_START], range_y[PLOT_END]])
    plt.legend(loc='best')

    # BUG:
    # When I show(block=False) or don't show() at all, the plt object somehow does not die and what happens is
    # the past plots are not discarded when drawing new plots.
    # When I show(block=True), the image does not get saved!

    # BUG FIX 1:
    # First save, then show(block = True)

    # BUG FIX 2:
    # Even better: after show(block=false)  call plt.gcf().clear(). Also might call plt.clf() plt.cla() plt.close().


    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    plt.savefig('./output/{}_{}_{}.png'.format(output_file_name, main_title, st))

    plt.show(block=True)
    # plt.show(block=False)
    plt.gcf().clear()


def plot_x_y_scatter(main_title, x_axis_tile, y_axis_title, subplotables, output_file_name):
    cmap = get_cmap(len(subplotables) + 1)

    for i, plotable in enumerate(subplotables):
        color = cmap(i)
        if constants.DEBUG_VERBOSE:
            print " color {} = {}".format(i, color)

        randoms_x_values = plotable.x_values[0:-1]
        randoms_y_values = plotable.y_values[0:-1]
        random_label = "{}{}".format("random ", plotable.label)
        smart_label = "{}{}".format("smart ", plotable.label)

        smart_x_values = [plotable.x_values[-1]]
        smart_y_values = [plotable.y_values[-1]]
        plt.scatter(randoms_x_values, randoms_y_values, color=color, label=random_label, marker='o')
        plt.scatter(smart_x_values, smart_y_values, color=color, label=smart_label, marker='s')

        # the dots
        # plt.plot(plotable.x_values, plotable.y_values, )

    plt.title(main_title)
    plt.xlabel(x_axis_tile)
    plt.ylabel(y_axis_title)

    # plt.axis([range_x[PLOT_START], range_x[PLOT_END], range_y[PLOT_START], range_y[PLOT_END]])
    plt.legend(loc='best')

    plt.grid(True)

    # BUG:
    # When I show(block=False) or don't show() at all, the plt object somehow does not die and what happens is
    # the past plots are not discarded when drawing new plots.
    # When I show(block=True), the image does not get saved!

    # BUG FIX 1:
    # First save, then show(block = True)

    # BUG FIX 2:
    # Even better: after show(block=false)  call plt.gcf().clear(). Also might call plt.clf() plt.cla() plt.close().


    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    plt.savefig('./output/{}_{}_{}.png'.format(output_file_name, main_title, st))

    # plt.show()
    plt.show(block=False)
    plt.gcf().clear()


def plot_x_y_line(main_title, x_axis_tile, y_axis_title, subplotables, output_file_name):
    cmap = get_cmap(len(subplotables) + 1)

    for i, plotable in enumerate(subplotables):
        color = cmap(i)
        if constants.DEBUG_VERBOSE:
            print " color {} = {}".format(i, color)

        ax = plt.gca()  # grab the current axis
        ar = numpy.arange(6)
        print "ar", ar
        ax.set_xticks(ar)



        print plotable.x_values
        print plotable.y_values
        # exit(0)
        ax.set_xticklabels(['a', '1', '2', '4', '8', '16'])

        xticks = ax.xaxis.get_major_ticks()
        print xticks[0].label1

        plt.plot([1, 2, 3, 4, 5], plotable.y_values, color=color, label=plotable.label, marker='o')


        # the dots
        # plt.plot(plotable.x_values, plotable.y_values, )

    plt.title(main_title)
    plt.xlabel(x_axis_tile)
    plt.ylabel(y_axis_title)

    plt.axis([1, 5, 0, 1])
    plt.legend(loc='best')

    plt.grid(True)

    # BUG:
    # When I show(block=False) or don't show() at all, the plt object somehow does not die and what happens is
    # the past plots are not discarded when drawing new plots.
    # When I show(block=True), the image does not get saved!

    # BUG FIX 1:
    # First save, then show(block = True)

    # BUG FIX 2:
    # Even better: after show(block=false)  call plt.gcf().clear(). Also might call plt.clf() plt.cla() plt.close().

    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    plt.savefig('./output/{}_{}_{}.png'.format(output_file_name, main_title, st))

    plt.show(block=False)
    # plt.show(block=True)
    plt.gcf().clear()



def barchart(objects, performance, y_label, title):
    y_pos = numpy.arange(len(objects))
    plt.bar(y_pos, performance, align='center', alpha=0.5)
    plt.xticks(y_pos, objects, fontsize=6, rotation=90)
    # plt.xticks(y_pos, objects)
    plt.ylabel(y_label)
    plt.title(title)


    plt.show(block=True)


def barchart_dual_y_shared_x(x, x_label, y1, y1_label, y2, y2_label, title):
    # Two subplots, the axes array is 1-d
    f, axarr = plt.subplots(2, sharex=True)

    x_pos = numpy.arange(len(x))
    plt.xticks(x_pos, x, fontsize=8, rotation=90)

    # plt.bar(y_pos, performance, align='center', alpha=0.5)
    axarr[0].bar(x_pos, y1, align='center')
    axarr[0].set_title(y1_label)
    axarr[1].set_title(y2_label)
    axarr[1].bar(x_pos, y2, align='center')

    # Fine-tune figure; distance subplots farther from each other.
    # f.subplots_adjust(hspace=0.3)

    plt.show()

def plot_two_sided_x_y_lines_withsubplots(main_title, x_axis_tile, y_axis_title_left, y_axis_title_right,
                                          mean_subplotables, output_file_name):
    cmap = get_cmap(len(mean_subplotables) + 1)

    color1 = cmap(0)
    if constants.DEBUG_VERBOSE:
        print " color {} = {}".format(1, color1)

    plotable1 = mean_subplotables[0]

    fig, ax1 = plt.subplots()  # grab the current axis
    ar = numpy.arange(6)
    print "ar:", ar
    ax1.set_xticks(ar)

    print "xvalues:", plotable1.x_values
    print "y values:", plotable1.y_values
    # exit(0)
    ax1.set_xticklabels(['a', '4', '8', '16', '32'])

    xticks = ax1.xaxis.get_major_ticks()
    # print xticks[0].label1

    ax1.set_ylabel(y_axis_title_left)
    ax1.set_ylim(ymin=0, ymax=1)
    ax1.plot([1, 2, 3, 4], plotable1.y_values, color=color1, label=plotable1.label, marker='o')
    ax1.tick_params('y', colors=color1)

    plotable2 = mean_subplotables[1]

    ax2= ax1.twinx()
    color2 = cmap(1)

    ax2.set_ylabel(y_axis_title_right)
    ax2.set_ylim(ymin=0, ymax=10)
    ax2.tick_params('y', colors=color2)
    ax2.plot([1, 2, 3, 4], plotable2.y_values, color=color2, label=plotable2.label, marker='o')


        # the dots
        # plt.plot(plotable.x_values, plotable.y_values, )



    plt.title("Performance for cassandra")
    print "xaxtitle:", x_axis_tile
    ax1.set_xlabel(x_axis_tile)

    # plt.axis([1, 4, 0, 1])
    # plt.legend(loc='best')

    plt.grid(True)

    # BUG:
    # When I show(block=False) or don't show() at all, the plt object somehow does not die and what happens is
    # the past plots are not discarded when drawing new plots.
    # When I show(block=True), the image does not get saved!

    # BUG FIX 1:
    # First save, then show(block = True)

    # BUG FIX 2:
    # Even better: after show(block=false)  call plt.gcf().clear(). Also might call plt.clf() plt.cla() plt.close().

    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    plt.savefig('./output/{}_{}_{}.png'.format(output_file_name, main_title, st))
    # fig.tight_layout()

    plt.show(block=True)
    # plt.show(block=True)
    plt.gcf().clear()


