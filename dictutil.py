import customtkinter
import analyzer
import fields

"""
Given a dictionary, returns the sum of all numbers in the dictionary and any subdictionaries, multiplied by the second element of any matching keys in the conversion dictionary.
This is exclusively for the calculation of point values for matches.
"""
def recursively_count_values_with_conversion(dictionary: dict, conversion: dict):
    value = 0

    print("yes")
    print(dictionary)
    print(conversion) #TODO: The problem is that the percentage needs to be calculated earlier in the pipeline by a recursive dict checker that finds percentages and calculates them

    for key in dictionary.keys():
        if type(dictionary[key]) == int:
            value += dictionary[key] * conversion[key][1]
        else:
            value += recursively_count_values_with_conversion(dictionary[key], conversion[key])

    return value

"""
Given a list of dictionaries, return a dictionary with the average of every element of the original dictionary list.
"""
def recursively_average_all_values(values: "list[dict]"):
    averages = {} # Will contain keys mapping to lists of values

    for value in values:
        recursively_add_values_to_average(value, averages)

    return averages

def recursively_add_values_to_average(dictionary, averages):
    for key in dictionary.keys():
        if type(dictionary[key]) == int:
            try:
                averages[key]
            except:
                averages[key] = []
            averages[key].append(dictionary[key])
        else:
            try:
                averages[key]
            except:
                averages[key] = {}
            recursively_add_values_to_average(dictionary[key], averages[key])


def recursively_generate_match_data_frame(master, unaveraged_elements, headerFont, titleFont, numberFont, header=None, depth=-1):
    frame = customtkinter.CTkFrame(master)
    frame.pack(side=customtkinter.TOP, fill=customtkinter.X)

    if header:
        frameHeader = customtkinter.CTkLabel(frame, text=("> " * depth) + header + (depth * " <"), font=headerFont)
        frameHeader.pack(fill=customtkinter.X)

    for element in unaveraged_elements.keys():
        if type(unaveraged_elements[element]) == list:
            values = unaveraged_elements[element]

            element_frame = customtkinter.CTkFrame(frame)
            element_frame.pack(fill=customtkinter.X)

            element_frame.grid_columnconfigure(0, weight=1)

            element_title = customtkinter.CTkLabel(element_frame, text=element, font=titleFont)
            element_title.grid(row=0, column=0)

            element_value = customtkinter.CTkLabel(element_frame, text=sum(values)/len(values), font=numberFont)
            element_value.grid(row=0, column=1)

            create_analysis_button(element_frame, element, values)

        elif type(unaveraged_elements[element]) == dict:
            recursively_generate_match_data_frame(frame, unaveraged_elements[element], headerFont, titleFont, numberFont, header=element, depth=depth+1)

def create_analysis_button(element_frame, element, values):
    element_analyze = customtkinter.CTkButton(element_frame, text="Analyze", command=lambda: analyzer.spawn_analyzer(element, values))
    element_analyze.grid(row=0, column=2)

def _compile_data_points(target_dictionary, source_dictionary):
        for key in source_dictionary.keys():
            if type(source_dictionary[key]) == int:
                target_dictionary[key] = source_dictionary[key]
            elif type(source_dictionary[key]) == dict:
                target_dictionary[key] = {}
                _compile_data_points(target_dictionary[key], source_dictionary[key])

def compile_team_data(matches):
    compiled_team_data = {}
    for match in matches:
        for team in match.keys():
            if not team in compiled_team_data.keys():
                compiled_team_data[team] = [{}]
            else:
                compiled_team_data[team].append({})
            _compile_data_points(compiled_team_data[team][-1], match[team])
    return compiled_team_data

def calculate_points(team_data):
    points_autonomous = []
    points_teleop = []
    points_total = []
    for match in team_data:
        points_autonomous.append(recursively_count_values_with_conversion(match["Autonomous"], fields.fields["Autonomous"]))
        points_teleop.append(recursively_count_values_with_conversion(match["Teleop"], fields.fields["Teleop"]))

    for i in range(0, len(points_autonomous)):
        points_total.append(points_autonomous[i] + points_teleop[i])

    average_autonomous = sum(points_autonomous) / len(points_autonomous)
    average_teleop = sum(points_teleop) / len(points_teleop)
    average_total = average_teleop + average_autonomous

    return points_autonomous, points_teleop, points_total

def calculate_point_averages(points_autonomous, points_teleop, points_total=None):
    average_autonomous = sum(points_autonomous) / len(points_autonomous)
    average_teleop = sum(points_teleop) / len(points_teleop)
    average_total = average_teleop + average_autonomous

    return average_autonomous, average_teleop, average_total

def convert_list_of_dict_to_dict_with_list(data):
    final_dict = {}

    for dictionary in data:

        for point in dictionary.keys():

            if not point in final_dict.keys():
                final_dict[point] = []
            final_dict[point].append(dictionary[point])

    for point in final_dict.keys():
        if type(final_dict[point][0]) == dict:
            final_dict[point] = convert_list_of_dict_to_dict_with_list(final_dict[point])

    return final_dict

def get_all_keys_as_paths(team_data):
    keys = []

    for point in team_data.keys():
        if type(team_data[point]) == list:
            keys.append(point)
        elif type(team_data[point]) == dict:
            subpaths = get_all_keys_as_paths(team_data[point])
            for subpath in subpaths:
                keys.append(point + "/" + subpath)

    return keys

def retrieve_nested_value_from_path(dictionary, value_path):
    path = value_path.split("/")
    for path_element in path:
        if not path_element in dictionary.keys(): return None
        if type(dictionary[path_element]) == dict:
            return retrieve_nested_value_from_path(dictionary[path_element], "/".join(path[1:]))
        else:
            return dictionary[path_element]