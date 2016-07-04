# trajectory = 1D array of posts/ locations/ or others
import datetime
import numpy

"""For posts sequences"""
def split_trajectory(trajectories, split_day = 1):
    print("[Trajectory] Splitting trajectories..., input #=", len(trajectories))
    split_time = 86400 * split_day
    sequences = []
    for a_trajectory in trajectories:
        if len(a_trajectory) > 0:
            i = 0
            while len(a_trajectory) > 1 and len(a_trajectory) - 1 > i:
                # if the time interval is larger than splitting threshold
                if a_trajectory[i+1].time - a_trajectory[i].time > split_time:
                    sequences.append(a_trajectory[:i+1]) # add the former sequence to sequences
                    a_trajectory = a_trajectory[i+1:] # keep working on the rest of the trajectory
                    i = 0
                else:
                    i += 1
            sequences.append(a_trajectory)
    print("  output sequences #=", len(sequences), " ,average length=", sum([len(x) for x in sequences]) / len(sequences))
    return sequences

def split_trajectory_byday(trajectories):
    print("[Trajectory] Splitting trajectories by day, input #=", len(trajectories))
    day_init = 1446336000 # 2015/11/01
    a_day = 86400
    sequences = []
    for a_trajectory in trajectories:
        trajectory_day = [datetime.datetime.fromtimestamp(int(x.time)).strftime('%Y-%m-%d') for x in a_trajectory]
        start_indicies = [i + 1 for i, x in enumerate(trajectory_day[1:]) if trajectory_day[i] != trajectory_day[i + 1]]
        sequences.extend([a_trajectory[i:j] for i, j in zip([0] + start_indicies, start_indicies + [None])])
    print("  output sequences #=", len(sequences), " ,average length=", sum([len(x) for x in sequences]) / len(sequences))
    return sequences

def get_vector_sequence(trajectories, attr = "membership"):
    print("[Trajectory] Getting vector sequences...")
    vector_sequences = []
    for a_sequence in trajectories:
        #a_vector_sequence = [locations[a_post.lid].membership for a_post in a_sequence]
        a_vector_sequence = [getattr(a_location, attr) for a_location in a_sequence]
        vector_sequences.append(a_vector_sequence)
    return vector_sequences

def get_cluster_sequence(trajectories, attr = "cluster"):
    cluster_sequences = []
    for a_sequence in trajectories:
        cluster_sequence = []
        for a_location in a_sequence:
            if len(cluster_sequence) == 0 or cluster_sequence[-1] != getattr(a_location, attr):
                cluster_sequence.append(getattr(a_location, attr))
        cluster_sequences.append(cluster_sequence)
    return cluster_sequences

"""For location sequences"""
def convertto_location_sequences(post_sequences, locations):
    location_sequences = []
    longest_len = 0
    for s in post_sequences:
        location_s = [locations[x.lid] for x in s]
        location_sequences.append(location_s)
        longest_len = max(longest_len, len(location_s))
    return location_sequences, longest_len

"""Transform to array"""
def get_vector_array(trajectories, trajectory_len, attr = "membership"):
    print("[Trajectory] Getting vector sequences...")
    attr_dim = getattr(trajectories[0][0], attr).shape[1]
    # set array = trajectories # * trajectory length * attr's dimension
    vector_array = numpy.zeros((len(trajectories), trajectory_len, attr_dim))
    for i, a_sequence in enumerate(trajectories):
        for j, a_location in enumerate(a_sequence):
            vector_array[i, j, :] = getattr(a_location, attr)
    return vector_array