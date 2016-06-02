# trajectory = list of posts

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

def get_vector_sequence(trajectories, locations, attr = "membership"):
    print("[Trajectory] Getting vector sequences...")
    vector_sequences = []
    for a_sequence in trajectories:
        #a_vector_sequence = [locations[a_post.lid].membership for a_post in a_sequence]
        a_vector_sequence = [getattr(locations[a_post.lid], attr) for a_post in a_sequence]
        vector_sequences.append(a_vector_sequence)
    return vector_sequences

def get_cluster_sequence(trajectories, locations, attr = "cluster"):
    cluster_sequences = []
    for a_sequence in trajectories:
        cluster_sequence = []
        for a_post in a_sequence:
            if len(cluster_sequence) == 0 or cluster_sequence[-1] != getattr(locations[a_post.lid], attr):
                cluster_sequence.append(getattr(locations[a_post.lid], attr))
        cluster_sequences.append(cluster_sequence)
    return cluster_sequences

"""For location sequences"""
def convertto_location_sequences(post_sequences, locations):
    location_sequences = []
    for s in post_sequences:
        location_s = [locations[x.lid] for x in s]
        location_sequences.append(location_s)
    return location_sequences