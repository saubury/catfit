import re
import argparse
from datetime import datetime


# Settings
demo_file_path = 'example.out'
cat_weight_min = 4500
cat_weight_max = 6100


# Globals
cat_was_on_scale = False
cat_entered_scale_date = datetime.now()
food_start_weight = 0
cat_weight_sample_total = 0
cat_weight_sample = 0


def do_update(event_date, cat_weight, food_weight):
    global cat_was_on_scale
    global cat_entered_scale_date
    global food_start_weight
    global cat_weight_sample_total
    global cat_weight_sample 

    if cat_weight_min <= cat_weight <= cat_weight_max:
        # Cat is on scale
        if ( not cat_was_on_scale ):
            # Cat just stepped onto scale
            cat_entered_scale_date = event_date
            food_start_weight = food_weight

        cat_was_on_scale = True
        cat_weight_sample_total = cat_weight_sample_total + cat_weight
        cat_weight_sample = cat_weight_sample + 1
    else:
        # Cat is not on scale
        if ( cat_was_on_scale ):
            # Cat just left
            cat_weight_avg = cat_weight_sample_total / cat_weight_sample
            # print('cat_weight_avg:{:,.0f}  cat_weight_sample_total:{} cat_weight_samples:{}'.format(cat_weight_avg, cat_weight_sample_total, cat_weight_sample))
            cat_weight_sample_total = 0
            cat_weight_sample = 0

            print('Cat departed,  From:{} To:{} FoodStart:{:,.0f} FoodEnd:{:,.0f} Duration:{} cat_weight_avg:{:,.0f}'.format(cat_entered_scale_date, event_date, food_start_weight, food_weight, event_date-cat_entered_scale_date, cat_weight_avg))

        cat_was_on_scale = False

def do_filedemo():
    with open(demo_file_path) as file_handle:
        line = file_handle.readline()
        while line:
            line_parts=re.split(r'(?=[A-Z])', line.strip())
            event_date_text=line_parts[0].strip()
            event_date = datetime.strptime(event_date_text, '%d/%m/%Y %H:%M:%S')
            cat_weight=re.sub(r'[^0-9]', '', line_parts[1])
            food_weight=re.sub(r'[^0-9\-]', '', line_parts[2])
            do_update(event_date, int(cat_weight), int(food_weight))
            line = file_handle.readline()


def main():
    parser = argparse.ArgumentParser(description='Cat monitor')
    parser.add_argument('--filedemo', help='run a demonstration from file', action='store_true')
    args = parser.parse_args()

    if args.filedemo:
        do_filedemo()
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
