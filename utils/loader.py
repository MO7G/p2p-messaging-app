import matplotlib.pyplot as plt

def calculate_links(n):
    return n * (n - 1) // 2

# Number of nodes (1 to 100)
nodes = list(range(1, 101))

# Calculate the number of links for each number of nodes
links = [calculate_links(n) for n in nodes]

# Plotting
plt.plot(nodes, links, label='Mesh Topology')
plt.xlabel('Number of Nodes')
plt.ylabel('Number of Links')
plt.title('Mesh Topology: Growth of Links with Nodes')
plt.legend()
plt.grid(True)
plt.show()
