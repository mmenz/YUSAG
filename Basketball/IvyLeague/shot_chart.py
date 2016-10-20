import argparse
import os
import csv
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Arc
import seaborn as sns


# Below functions taken from
# https://github.com/danielwelch/nbaShotCharts
def draw_court(ax=None, color='gray', lw=1, outer_lines=False):
    """
    Returns an axes with a basketball court drawn onto to it.
    This function draws a court based on the x and y-axis values that the NBA
    stats API provides for the shot chart data.  For example, the NBA stat API
    represents the center of the hoop at the (0,0) coordinate.  Twenty-two feet
    from the left of the center of the hoop in is represented by the (-220,0)
    coordinates.  So one foot equals +/-10 units on the x and y-axis.
    TODO: explain the parameters
    """
    if ax is None:
        ax = plt.gca()

    # Create the various parts of an NBA basketball court

    # Create the basketball hoop
    hoop = Circle((0, 0), radius=7.5, linewidth=lw, color=color, fill=False)

    # Create backboard
    backboard = Rectangle((-30, -7.5), 60, -1, linewidth=lw, color=color)

    # The paint
    # Create the outer box 0f the paint, width=16ft, height=19ft
    outer_box = Rectangle((-80, -47.5), 160, 190, linewidth=lw, color=color,
                          fill=False)
    # Create the inner box of the paint, widt=12ft, height=19ft
    inner_box = Rectangle((-60, -47.5), 120, 190, linewidth=lw, color=color,
                          fill=False)

    # Create free throw top arc
    top_free_throw = Arc((0, 142.5), 120, 120, theta1=0, theta2=180,
                         linewidth=lw, color=color, fill=False)
    # Create free throw bottom arc
    bottom_free_throw = Arc((0, 142.5), 120, 120, theta1=180, theta2=0,
                            linewidth=lw, color=color, linestyle='dashed')
    # Restricted Zone, it is an arc with 4ft radius from center of the hoop
    restricted = Arc((0, 0), 80, 80, theta1=0, theta2=180, linewidth=lw,
                     color=color)

    # Three point line
    # Create the right side 3pt lines, it's 14ft long before it arcs
    corner_three_a = Rectangle((-220, -47.5), 0, 140, linewidth=lw,
                               color=color)
    # Create the right side 3pt lines, it's 14ft long before it arcs
    corner_three_b = Rectangle((220, -47.5), 0, 140, linewidth=lw, color=color)
    # 3pt arc - center of arc will be the hoop, arc is 23'9" away from hoop
    three_arc = Arc((0, 0), 475, 475, theta1=22, theta2=158, linewidth=lw,
                    color=color)

    # Center Court
    center_outer_arc = Arc((0, 422.5), 120, 120, theta1=180, theta2=0,
                           linewidth=lw, color=color)
    center_inner_arc = Arc((0, 422.5), 40, 40, theta1=180, theta2=0,
                           linewidth=lw, color=color)

    # List of the court elements to be plotted onto the axes
    court_elements = [hoop, backboard, outer_box, inner_box, top_free_throw,
                      bottom_free_throw, restricted, corner_three_a,
                      corner_three_b, three_arc, center_outer_arc,
                      center_inner_arc]

    if outer_lines:
        # Draw the half court line, baseline and side out bound lines
        outer_lines = Rectangle((-250, -47.5), 500, 470, linewidth=lw,
                                color=color, fill=False)
        court_elements.append(outer_lines)

    # Add the court elements onto the axes
    for element in court_elements:
        ax.add_patch(element)

    return ax


def shot_chart(x, y, title="", kind="scatter", color="b", cmap=None,
               xlim=(-250, 250), ylim=(422.5, -47.5),
               court_color="gray", outer_lines=False, court_lw=1,
               flip_court=False, kde_shade=True, hex_gridsize=None,
               ax=None, **kwargs):
    """
    Returns an Axes object with player shots plotted.
    TODO: explain the parameters
    """

    if ax is None:
        ax = plt.gca()

    if cmap is None:
        cmap = sns.light_palette(color, as_cmap=True)

    if not flip_court:
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
    else:
        ax.set_xlim(xlim[::-1])
        ax.set_ylim(ylim[::-1])

    ax.tick_params(labelbottom="off", labelleft="off")
    ax.set_title(title, fontsize=18)

    draw_court(ax, color=court_color, lw=court_lw, outer_lines=outer_lines)

    if kind == "scatter":
        ax.scatter(x, y, **kwargs)

    elif kind == "kde":
        sns.kdeplot(x, y, shade=kde_shade, cmap=cmap,
                    ax=ax, **kwargs)
        ax.set_xlabel('')
        ax.set_ylabel('')

    elif kind == "hex":
        if hex_gridsize is None:
            # Get the number of bins for hexbin using Freedman-Diaconis rule
            # This is idea was taken from seaborn, which got the calculation
            # from http://stats.stackexchange.com/questions/798/
            from seaborn.distributions import _freedman_diaconis_bins
            x_bin = _freedman_diaconis_bins(x)
            y_bin = _freedman_diaconis_bins(y)
            hex_gridsize = int(np.mean([x_bin, y_bin]))

        ax.hexbin(x, y, gridsize=hex_gridsize, cmap=cmap, **kwargs)

    else:
        raise ValueError("kind must be 'scatter', 'kde', or 'hex'.")

    return ax

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('player', metavar='PLAYER', type=str)
    parser.add_argument('--data_dir', type=str, default='output/')
    args = parser.parse_args()

    player_x = []
    player_y = []
    colors = []

    def color_func(made_or_missed):
        return 'green' if made_or_missed == 'made' else 'red'

    def convert_x(row):
        x, y = int(row['x']), int(row['y'])
        return y * 500.0 / 50.0 - 250.0

    def convert_y(row):
        x, y = int(row['x']), int(row['y'])
        # switch if on other side of court
        # BE CAREFUL HERE, STILL NEED TO ACCOUNT FOR END OF HALF SHOTS
        if x > 47.0:
            x = 94 - x
        return x * 500.0 / 47.0 - 47.5

    filenames = os.listdir(args.data_dir)
    for filename in filenames:
        with open(os.path.join(args.data_dir, filename)) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['shooter'] == args.player:
                    player_x.append(convert_x(row))
                    player_y.append(convert_y(row))
                    colors.append(color_func(row['result']))

    print len(player_x), 'shots'
    ax = shot_chart(player_x, player_y, c=colors, s=30, kind='scatter')
    plt.show()
