# trajectory = 1D array of posts/ locations/ or others
import datetime
import numpy
from pytz import timezone

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
    time_zone = timezone('America/New_York')
    sequences = []
    for a_trajectory in trajectories:
        trajectory_day = [datetime.datetime.fromtimestamp(int(x.time), tz=time_zone).strftime('%Y-%m-%d') for x in a_trajectory]
        start_indicies = [i for i in range(1, len(trajectory_day)) if trajectory_day[i] != trajectory_day[i - 1]]
        sequences.extend([a_trajectory[i:j] for i, j in zip([0] + start_indicies, start_indicies + [None])])
    print("  output sequences #=", len(sequences), " ,average length=", sum([len(x) for x in sequences]) / len(sequences))
    return sequences

def remove_adjacent_location(trajectories):
    print("[Trajectory] Removing adjacent same locations")
    for i in range(len(trajectories)):
        trajectories[i] = [trajectories[i][j] for j in range(1, len(trajectories[i])) if trajectories[i][j].lid != trajectories[i][j - 1].lid]
    print("  average length after remove=", sum([len(x) for x in trajectories]) / len(trajectories))
    return trajectories

def remove_short(trajectories, threshold = 2):
    print("[Trajectory] Removing short trajectories, input #=", len(trajectories))
    fail_indices = []
    for i, s in enumerate(trajectories):
        if len(s) <= threshold:
            fail_indices.append(i)
    trajectories = numpy.delete(numpy.array(trajectories), fail_indices)
    print("  delete #:", len(fail_indices), " ,remain sequences #:", len(trajectories))
    print("  avg, std=", sum([len(x) for x in trajectories]) / len(trajectories), numpy.std([len(x) for x in trajectories]))
    return trajectories

def get_cluster_sequence(trajectories, attr, attr2 = None):
    print("[Trajectory] Getting cluster sequences...")
    # set array = trajectories # * trajectory length * attr's dimension
    attr_sequences = []
    attr2_sequences = []
    removes = []
    for i in range(len(trajectories)):
        a_sequence = [getattr(x, attr) for x in trajectories[i]]
        if attr2:
            a_sequence2 = [getattr(x, attr2) for x in trajectories[i]]
            remove = [j for j in range(1, len(trajectories[i])) if a_sequence[j] == a_sequence[j - 1] and a_sequence2[j] == a_sequence2[j - 1]]
        else:
            remove = [j for j in range(1, len(trajectories[i])) if a_sequence[j] == a_sequence[j - 1]]
        removes.append(remove)
        a_sequence = numpy.delete(numpy.array(a_sequence), remove)
        attr_sequences.append(a_sequence)
        if attr2:
            a_sequence2 = numpy.delete(numpy.array(a_sequence2), remove)
            attr2_sequences.append(a_sequence2)
    print("  avg, std=", sum([len(x) for x in attr_sequences]) / len(attr_sequences), numpy.std([len(x) for x in attr_sequences]))
    return removes,  attr_sequences, attr2_sequences

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
    vector_array[:,:,:] = float('nan')
    for i in range(len(trajectories)):
        for j in range(len(trajectories[i])):
            vector_array[i, j, :] = getattr(trajectories[i][j], attr)
    return vector_array

"""Output"""
def output_clusters(post_sequences, membership, u, file_path):
    time_zone = timezone('America/New_York')
    membership = numpy.argmax(u, axis=0)
    print("[trajectory] outputing clusters...")
    for c in range(u.shape[0]):
        indices = [i for i, x in enumerate(membership) if x == c]
        if len(indices) is not 0:
            f = open(file_path + "_" + str(c) + ".txt", "w")
            f.write(str(c) + ">\t#:" + str(len(indices)) + "\tall s avg:" + str((u[c,:].sum() / u.shape[1])) + "\n")
            sorted_indices = sorted(indices, key=lambda x:u[c, x])
            sorted_indices = sorted_indices[::-1]
            for i in sorted_indices:
                f.write(str(u[c, i]) + "\t> ")
                for a_post in post_sequences[i]:
                    tag_str = ".".join(a_post.tags)
                    f.write("(" + datetime.datetime.fromtimestamp(int(a_post.time), tz=time_zone).strftime('%Y-%m-%d %H:%M') +
                        ", " + a_post.lname + " >" + a_post.lid + ", <" + tag_str + ">), ")
                f.write("\n")
            f.close()