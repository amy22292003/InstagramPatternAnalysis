# trajectory = list of Locations

"""For posts sequences"""
def split_trajectory(trajectories, split_day = 1):
    print("[Trajectory] Splitting trajectories..., input #=", len(trajectories))
    split_time = 86400 * split_day
    sequences = []
    for a_trajectory in trajectories:
        if len(a_trajectory) > 0:
            i = 0
            while len(a_trajectory) > 1 & len(a_trajectory) - 1 > i:
                # if the time interval is larger than splitting threshold
                if a_trajectory[i+1].time - a_trajectory[i].time > split_time:
                    sequences.append(a_trajectory[:i+1]) # add the former sequence to sequences
                    a_trajectory = a_trajectory[i+1:] # keep working on the rest of the trajectory
                    i = 0
                else:
                    i += 1
            sequences.append(a_trajectory)
    print("--output sequences #=", len(sequences), " ,average length=", sum([len(x) for x in sequences]) / len(sequences))
    return sequences

def get_vector_sequence(trajectories, locations):
    print("[Trajectory] Getting vector sequences...")
    vector_sequences = []
    for a_sequence in trajectories:
        a_vector_sequence = [locations[a_post.lid].membership for a_post in a_sequence]
        vector_sequences.append(a_vector_sequence)
    print("vs:", type(vector_sequences[0]), type(vector_sequences[0][0]))
    return vector_sequences