import pandas as pd
import numpy as np

def data_preparation(data_input):

	#remove less usefull column
	data_input = data_input.drop(columns='number')
	#there is no clear meaning on how the entry is being numbered / ordered

    #remove duplicates
	duplicate = data_input.duplicated()
	duplicate = duplicate.reset_index()
	for a in duplicate['index']:
		check = duplicate.iloc[a,1]
		if check == True:
			data_input = data_input.drop(a)
			# print(data_input.iloc[a])

	#split date
	date_split = data_input['date'].str.split(pat="-",expand=True)
	data_input["date_year"] = date_split[0].astype('int64')
	data_input["date_month"] = date_split[1].astype('int64')
	data_input["date_day"] = date_split[2].astype('int64')

	#clean price and change type
	data_input['price'] = data_input['price'].str.replace(pat="Not available",repl="NaN",regex=False)
	data_input['price'] = data_input['price'].str.replace(pat=",",repl="",regex=False)
	data_input['price'] = data_input['price'].str.replace(pat="$",repl="",regex=False)
	data_input['price'] = data_input['price'].astype('float64')
	# missing value - replace missing price with the previous price of same item name
	data_input['price'] = data_input.groupby('name')['price'].fillna(method='ffill')

	#change n_reviews type
	data_input['n_reviews'] = data_input['n_reviews'].str.replace(pat="No customer reviews yet",repl="NaN",regex=False)
	#convert into float to process missing value first
	data_input['n_reviews'] = data_input['n_reviews'].str.replace(pat=",",repl="",regex=False)
	data_input['n_reviews'] = data_input['n_reviews'].astype('float64')
	# missing value - replace missing review and rating with the previous value of same item name
	data_input['n_reviews'] = data_input.groupby('name')['n_reviews'].fillna(method='ffill')
	#convert into integer
	data_input['n_reviews'] = data_input['n_reviews'].replace(np.nan,0)
	data_input['n_reviews'] = data_input['n_reviews'].astype('int64')

	#convert rating type
	data_input['rating'] = data_input['rating'].str.replace(pat="Not available",repl="NaN",regex=False)
	data_input['rating'] = data_input['rating'].astype('float64')
	data_input['rating'] = data_input.groupby('name')['rating'].fillna(method='ffill')

	return data_input

def filter_low_review_entry (data_input, treshold):
	low_rating = data_input['n_reviews'] < treshold
	filtered_entry = data_input[~low_rating]
	return filtered_entry

def count_item_with_no_reviews(data_input):
	no_review = data_input[data_input['n_reviews'] == 0]
	total_no_review = no_review['name'].count()
	percentage = total_no_review / data_input['name'].count() * 100
	unique_item = no_review['name'].unique()
	recap = "In total there are " + str(total_no_review) + " items without review (" + str(round(percentage,2)) + "% total entry) spreaded among " + str(unique_item.shape[0]) + " unique item."
	print(recap)
	##check the items which have 0 review
	# inconsistent_item = []
	# for item in unique_item:
	# 	total = 0
	# 	count_non_null = 0
	# 	item_with_same_name = data_input[data_input['name'] == item]
	# 	for entry in item_with_same_name.itertuples():
	# 		if entry[4] != 0:
	# 			total += entry[4]
	# 			count_non_null += 1
	# 	print(str(total) + " from " + str(count_non_null))
	# 	if count_non_null != 0:
	# 		inconsistent_item.append(item)
	# print(inconsistent_item)
	# for item in inconsistent_item:
	# 	print(item)
	# 	print(data_input[data_input['name'] == item]['n_reviews'])


def print_item_detail(data_input, item_name):
	print("===== ITEM DETAIL =====")
	item_entry = data_input[data_input['name'] == item_name]
	print("Item Name: " + item_name)
	total_day_on_list = item_entry['date'].nunique()
	print("Day on Top 100 List: " + str(total_day_on_list))
	first_day_on_list = item_entry['date'].sort_index(ascending=True).iloc[0]
	print("First Day on Top 100 List: " + str(first_day_on_list))
	last_day_on_list = item_entry['date'].sort_index(ascending=False).iloc[0]
	print("Last Day on Top 100 List: " + str(last_day_on_list))
	lowest_price = item_entry['price'].min()
	print("Lowest Recorded Price: $" + str(lowest_price))
	highest_price = item_entry['price'].max()
	print("Highest Recorded Price: $" + str(highest_price))
	review_growth = item_entry[item_entry['date'] == last_day_on_list]['n_reviews'].max() - item_entry[item_entry['date'] == first_day_on_list]['n_reviews'].max()
	# review_growth = item_entry['n_reviews'].max() - item_entry['n_reviews'].min()
	print("Review Growth: " + str(review_growth))
	average_rating = item_entry['rating'].mean()
	print("Average Rating: " + str(round(average_rating,2)))

def top_price_analysis(data_input):
	max_price = data_input['price'].max()
	highest_price_item = data_input[data_input['price'] == max_price]['name'].value_counts().index
	print(" \n----------------------------------------------------------------")
	print("HIGHEST PRICE ANALYSIS")
	for item_name in highest_price_item:
		print('\n')
		print_item_detail(data_input,item_name)
		highest_date = data_input[(data_input['name'] == item_name) & (data_input['price'] == max_price)]['date']
		print("This item reach the highest price $" + str(max_price) + " at:")
		for date_point in highest_date:
			print(date_point)

def bottom_price_analysis(data_input):
	min_price = data_input['price'].min()
	lowest_price_item = data_input[data_input['price'] == min_price]['name'].value_counts().index
	print("\n----------------------------------------------------------------")
	print("LOWEST PRICE ANALYSIS")
	for item_name in lowest_price_item:
		print('\n')
		print_item_detail(data_input,item_name)
		lowest_date = data_input[(data_input['name'] == item_name) & (data_input['price'] == min_price)]['date']
		print("This item reach the lowest price $" + str(min_price) + " at:")
		for date_point in lowest_date:
			print(date_point)

def most_frequent_item_analysis(data_input):
	list_of_frequeuncy = data_input.groupby('name')['date'].nunique()
	most_occurance = list_of_frequeuncy.max()
	item_with_most_occurance = list_of_frequeuncy[list_of_frequeuncy == most_occurance].index
	print("\n----------------------------------------------------------------")
	print("MOST FREQUENTLY LISTED ITEM")
	for item_name in item_with_most_occurance:
		print('\n')
		print_item_detail(data_input,item_name)

def most_reviewed_item(data_input):
	highest_review = data_input['n_reviews'].max()
	highest_review_item = data_input[data_input['n_reviews'] == highest_review]['name'].value_counts().index
	print("\n----------------------------------------------------------------")
	print("MOST REVIEWED ITEM")
	for item_name in highest_review_item:
		print('\n')
		print_item_detail(data_input,item_name)
		most_review_date = data_input[(data_input['name'] == item_name) & (data_input['n_reviews'] == highest_review)]['date']
		print("This item reach the most review with " + str(highest_review) + " total reviews at:")
		for date_point in most_review_date:
			rating_on_highest_review = data_input[(data_input['name'] == item_name) & (data_input['date'] == date_point)]['rating'].iloc[0]
			print(date_point + " with " + str(rating_on_highest_review) + " rating")

def daily_summary(data_input, date_input):
	print("\n== DAILY SUMMARY FOR " + date_input + " ==\n")
	daily_data = data_input[data_input['date'] == date_input]
	highest_price = daily_data['price'].max()
	print("# Item with Highest Price is " + daily_data[daily_data['price'] == highest_price]['name'].iloc[0] + " with $" + str(highest_price))
	lowest_price = daily_data['price'].min()
	print("# Item with Lowest Price is " + daily_data[daily_data['price'] == lowest_price]['name'].iloc[0] + " with $" + str(lowest_price))
	most_review = daily_data['n_reviews'].max()
	print("# Item with Most Review is " + daily_data[daily_data['n_reviews'] == most_review]['name'].iloc[0] + " with " + str(most_review) + " review")
	rated_5_item = daily_data[daily_data['rating'] == 5]['name']
	print("# In this date, " + str(rated_5_item.nunique()) + " item have 5 rating.")
	if rated_5_item.nunique() != 0:
		print("  Which are :")
	for item_name in rated_5_item.value_counts().index:
		print("  - " + item_name) 

def main():
    electronics = pd.read_csv("dataset.csv")
    electronics = data_preparation(electronics)
    count_item_with_no_reviews(electronics)
    # electronics = filter_low_review_entry(electronics, 10)
    # top_price_analysis(electronics)
    # bottom_price_analysis(electronics)
    # most_frequent_item_analysis(electronics)
    # most_reviewed_item(electronics)
    # first_record_day = electronics['date'].min()
    # daily_summary(electronics,first_record_day)
    # last_record_day = electronics['date'].max()
    # daily_summary(electronics,last_record_day)
    # date_with_5_rating = electronics[electronics['rating'] == 5]['date'].iloc[0]
    # daily_summary(electronics,date_with_5_rating)
    # march_data = electronics[electronics['date_month'] == 2]
    # most_reviewed_item(march_data)

if __name__ == "__main__":
    main()