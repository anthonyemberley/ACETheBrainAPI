from __future__ import division
from models import Response
import math

import warnings

min_number_responses = 3

def get_all_question_responses(question, user_id):
	responses = Response.query.filter_by(question=question, user_id=user_id)
	print responses.count()
	return responses

def get_response_features(response):
	errors = int(response.errors)
	pauses = int(response.pauses)
	response_time = int(response.response_time)
	response_length = len(response.response)

	return(errors, pauses, response_time, response_length)

def euclidian_distance(response1, response2):
	# r1_features = get_response_features(response1)
	# r2_features = get_response_features(response2)
	total = 0
	for i in range(len(response1)):
		mini_sum = math.pow(response1[i] - response2[i], 2)
		total += mini_sum
	return math.sqrt(total)


class LOF:
    """Helper class for performing LOF computations and instances normalization."""
    def __init__(self, responses, question, normalize=True, distance_function=euclidian_distance):
        self.responses = responses
        self.normalize = normalize
        self.distance_function = distance_function
        self.question = question
        #Each response is a tuple of the form: (errors, pauses, response_time, response_length)
        responseValues = []
        for response in responses:
        	features = get_response_features(response)
        	responseValues.append(features)
        self.responseValues = responseValues
        if normalize:
            self.normalize_responses()

    def compute_response_attribute_bounds(self):
        min_values = [float("inf")] * len(self.responseValues[0]) #n.ones(len(self.instances[0])) * n.inf
        max_values = [float("-inf")] * len(self.responseValues[0]) #n.ones(len(self.instances[0])) * -1 * n.inf
        for response in self.responseValues:
            min_values = tuple(map(lambda x,y: min(x,y), min_values,response)) #n.minimum(min_values, instance)
            max_values = tuple(map(lambda x,y: max(x,y), max_values,response)) #n.maximum(max_values, instance)

        diff = [dim_max - dim_min for dim_max, dim_min in zip(max_values, min_values)]
        if not all(diff):
            problematic_dimensions = ", ".join(str(i+1) for i, v in enumerate(diff) if v == 0)
            warnings.warn("No data variation in dimensions: %s. You should check your data or disable normalization." % problematic_dimensions)

        self.max_attribute_values = max_values
        self.min_attribute_values = min_values

    def normalize_responses(self):
        """Normalizes the instances and stores the infromation for rescaling new instances."""
        if not hasattr(self, "max_attribute_values"):
            self.compute_response_attribute_bounds()
        new_responses = []
        for response in self.responseValues:
            new_responses.append(self.normalize_response(response)) # (instance - min_values) / (max_values - min_values)
        self.responseValues = new_responses

    def normalize_response(self, responseValue):
        return tuple(map(lambda value,max,min: (value-min)/(max-min) if max-min > 0 else 0,
                         responseValue, self.max_attribute_values, self.min_attribute_values))

    def local_outlier_factor(self, min_pts, responseValue):
        """The (local) outlier factor of instance captures the degree to which we call instance an outlier.
        min_pts is a parameter that is specifying a minimum number of instances to consider for computing LOF value.
        Returns: local outlier factor
        Signature: (int, (attr1, attr2, ...), ((attr_1_1, ...),(attr_2_1, ...), ...)) -> float"""
        if self.normalize:
            response = self.normalize_response(responseValue)
        return local_outlier_factor(min_pts, response, self.responseValues, distance_function=self.distance_function)





def k_distance(k, response, responses, distance_function=euclidian_distance):
    #TODO: implement caching
    """Computes the k-distance of instance as defined in paper. It also gatheres the set of k-distance neighbours.
    Returns: (k-distance, k-distance neighbours)
    Signature: (int, (attr1, attr2, ...), ((attr_1_1, ...),(attr_2_1, ...), ...)) -> (float, ((attr_j_1, ...),(attr_k_1, ...), ...))"""
    distances = {}
    for response2 in responses:
        distance_value = distance_function(response, response2)
        if distance_value in distances:
            distances[distance_value].append(response2)
        else:
            distances[distance_value] = [response2]
    distances = sorted(distances.items())
    neighbours = []
    [neighbours.extend(n[1]) for n in distances[:k]]
    k_distance_value = distances[k - 1][0] if len(distances) >= k else distances[-1][0]
    return k_distance_value, neighbours

def reachability_distance(k, response1, response2, responses, distance_function=euclidian_distance):
    """The reachability distance of instance1 with respect to instance2.
    Returns: reachability distance
    Signature: (int, (attr_1_1, ...),(attr_2_1, ...)) -> float"""
    (k_distance_value, neighbours) = k_distance(k, response2, responses, distance_function=distance_function)
    return max([k_distance_value, distance_function(response1, response2)])

def local_reachability_density(min_pts, response, responses, **kwargs):
    """Local reachability density of instance is the inverse of the average reachability
    distance based on the min_pts-nearest neighbors of instance.
    Returns: local reachability density
    Signature: (int, (attr1, attr2, ...), ((attr_1_1, ...),(attr_2_1, ...), ...)) -> float"""
    (k_distance_value, neighbours) = k_distance(min_pts, response, responses, **kwargs)
    reachability_distances_array = [0]*len(neighbours) #n.zeros(len(neighbours))
    for i, neighbour in enumerate(neighbours):
        reachability_distances_array[i] = reachability_distance(min_pts, response, neighbour, responses, **kwargs)
    if not any(reachability_distances_array):
        warnings.warn("Response %s (could be normalized) is identical to all the neighbors. Setting local reachability density to inf." % repr(response))
        return float("inf")
    else:
        return len(neighbours) / sum(reachability_distances_array)

def local_outlier_factor(min_pts, response, responses, **kwargs):
    """The (local) outlier factor of instance captures the degree to which we call instance an outlier.
    min_pts is a parameter that is specifying a minimum number of instances to consider for computing LOF value.
    Returns: local outlier factor
    Signature: (int, (attr1, attr2, ...), ((attr_1_1, ...),(attr_2_1, ...), ...)) -> float"""
    (k_distance_value, neighbours) = k_distance(min_pts, response, responses, **kwargs)
    instance_lrd = local_reachability_density(min_pts, response, responses, **kwargs)
    lrd_ratios_array = [0]* len(neighbours)
    for i, neighbour in enumerate(neighbours):
        responses_without_response = set(responses)
        responses_without_response.discard(neighbour)
        neighbour_lrd = local_reachability_density(min_pts, neighbour, responses_without_response, **kwargs)
        lrd_ratios_array[i] = neighbour_lrd / instance_lrd
    return sum(lrd_ratios_array) / len(neighbours)

def outliers(k, responses, **kwargs):
    """Simple procedure to identify outliers in the dataset."""
    responses_value_backup = responses
    outliers = []
    for i, response in enumerate(responses_value_backup):
        responses = list(responses_value_backup)
        responses.remove(response)
        l = LOF(responses, **kwargs)
        value = l.local_outlier_factor(k, response)
        if value > 1:
            outliers.append({"lof": value, "response": response, "index": i})
    outliers.sort(key=lambda o: o["lof"], reverse=True)
    return outliers


def get_local_outlier_factor(question, response, user_id):
	responses = get_all_question_responses(question, user_id)
	if responses.count() < min_number_responses:
		return "Not enough responses"
	lof = LOF(responses, question, True, euclidian_distance)
	responseValue = get_response_features(response)
	local_outlier_factor = lof.local_outlier_factor(min_number_responses, responseValue)
	print local_outlier_factor
	return local_outlier_factor


