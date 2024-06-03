#!/usr/bin/env python3
import tkinter as tk
import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import calendar
from collections import defaultdict

def calculate_time_between_events(json_data):
    date_time_map = {}
    from_stamp = None
    cumulative_total = 0

    for event in json_data:
        if all(key in event for key in ("fromState", "toState", "timestamp")):
            if event["fromState"] in ("idle", "rest") and event["toState"] == "work":
                from_stamp = event["timestamp"]
                from_day = datetime.fromtimestamp(from_stamp).strftime('%d-%m-%Y')
                date_time_map.setdefault(from_day, [0, 0])
            elif event["fromState"] == "work" and event["toState"] in ("idle", "rest"):
                if from_stamp is not None:
                    to_stamp = event["timestamp"]
                    time_difference = (to_stamp - from_stamp)
                    cumulative_total += time_difference
                    from_day = datetime.fromtimestamp(from_stamp).strftime('%d-%m-%Y')
                    date_time_map[from_day][0] += time_difference
                    date_time_map[from_day][1] = cumulative_total
                    from_stamp = None

    return date_time_map


def parse_data():
    with open('/Users/void/Library/Containers/com.github.ivoronin.TomatoBar/Data/Library/Caches/TomatoBar.log', 'r') as file:
        json_data = [json.loads(line) for line in file]

    return calculate_time_between_events(json_data)

def plot_dictionary_data(x_values, y_values_min, y_values_cum, weeks, total_hours, streak):

    fig, axs = plt.subplots(2, 2, figsize=(10, 8))
    fig.patch.set_facecolor('black')

    # Plot the first bar plot (total hours per week)
    axs[0, 0].bar(weeks, total_hours, color='tab:red', label='Time in hours')
    style_axes(axs[0, 0], 'Total hours per week')
    axs[0, 0].tick_params(axis='x', labelsize=5)

    # Plot the second line plot
    axs[0, 1].plot(x_values, y_values_cum, color='tab:green', label='Total time', linestyle='-', linewidth=3)
    style_axes(axs[0, 1], 'Total time in hours')
    axs[0, 1].tick_params(axis='x', labelbottom=False)
    axs[0, 1].tick_params(axis='y', labelleft=False)

    # Plot the third bar plot (daily time in minutes)
    axs[1, 0].bar(x_values, y_values_min, color='tab:blue', label='Time in minutes')
    style_axes(axs[1, 0], 'Daily time in minutes')
    axs[1, 0].tick_params(axis='x', rotation=90, labelsize=6)

    # Plot the fourth graph (text box with total time)
    axs[1, 1].text(0.5, 0.5, f"Streak for {streak} days\nTotal Time: {y_values_cum[-1]:.2f} hours\nToday's Time: {y_values_min[-1]:.2f} minutes",
                   horizontalalignment='center', verticalalignment='center', fontsize=18, transform=axs[1, 1].transAxes, color='white')
    timern = datetime.now().strftime('%H:%M:%S - %d/%m/%Y')
    axs[1, 1].text(1.0, 0.0, f"Updated {timern}", horizontalalignment='center', verticalalignment='center', fontsize=8, transform=axs[1, 1].transAxes, color='white')


    axs[1, 1].axis('off')

    plt.tight_layout()
    #plt.savefig('graph.png')
    plt.show()

def style_axes(ax, title):
    ax.set_facecolor('black')
    ax.set_title(title, color='white')
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')

def calculate_streak(data):
    sorted_dates = sorted(data.keys(), key=lambda date: datetime.strptime(date, '%d-%m-%Y'))
    current_streak = 0
    max_streak = 0

    for date in sorted_dates:
        if data[date][0] / 60 > 5:
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 0

    return max_streak
def calculate_values_for_graphs(data):
    x_values = list(data.keys())
    y_values_min = []
    y_values_cum = []

    total_hours_by_week = {}
    current_week_start = None

    for day, time_data in data.items():
        y_values_min.append(data[day][0] / 60)
        y_values_cum.append(data[day][1] / 3600)

        current_date = datetime.strptime(day, '%d-%m-%Y')
        current_week_start = current_date - timedelta(days=current_date.weekday())
        week_key = f"{current_week_start.strftime('%d %b')} - {current_week_start.strftime('%d %b')}"
        if week_key not in total_hours_by_week:
            total_hours_by_week[week_key] = 0
        total_hours_by_week[week_key] += time_data[0] / 3600

    # Add current day if it is not in the data
    current_day = datetime.now().strftime('%d-%m-%Y')
    if current_day not in data:
        y_values_min.append(0)
        y_values_cum.append(y_values_cum[-1])
        x_values.append(current_day)

    weeks, total_hours = zip(*total_hours_by_week.items())
    
    return x_values, y_values_min, y_values_cum, weeks, total_hours

if __name__ == "__main__":
    results = parse_data()
    x_values, y_values_min, y_values_cum, weeks, total_hours = calculate_values_for_graphs(results)
    streak = calculate_streak(results)
    plot_dictionary_data(x_values, y_values_min, y_values_cum, weeks, total_hours, streak)

