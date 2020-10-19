import math

import IPython
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.path as mpltPath

# f(n) = g(n) + h(n)
# g(n) bisherige pfadkosten
# h(n) geschätzte kosten zum ziel

# f(s) = h(s)
# f(z) = g(z)

grid = {
	"dimensions": [
		[-2, -2],
		[18, 18]
	],
	"path": {
		"start": [0, 0],
		"target": [16, 16]
	},
	"obstacle": [
		[3, 11],
		[11, 11],
		[11, 6],
		[13, 6],
		[13, 13],
		[3, 13],
		[3, 11],
	]
}


def obstacle(definition):
	xs, ys = zip(*definition)
	inside = []
	poly = mpltPath.Path(definition + [definition[0]], closed=True)
	for x in range(min(xs), max(xs) + 1):
		for y in range(min(ys), max(ys) + 1):
			#        plt.plot(x,y, 'yo')
			if poly.contains_point((x, y), radius=0.5):
				inside.append((x, y))
	#                plt.plot(x,y, 'rx')
	return inside


def h(node, target):
	return math.sqrt((node[0] - target[0]) ** 2 + (node[1] - target[1]) ** 2)


def get_neighbours(node):
	neighbours = []
	for x in range(max(-2, node[0] - 1), min(node[0] + 1, 18) + 1):
		for y in range(max(-2, node[1] - 1), min(node[1] + 1, 18) + 1):
			candidate = (x, y)
			if candidate == node:
				continue
			if candidate not in blocked:
				neighbours.append(candidate)
	return neighbours


fig = plt.figure()
ax = fig.add_subplot(1, 1, 1, aspect="equal", xlim=(-2, 18), ylim=(-2, 18))

ax.plot(0, 0, 'rx', 16, 16, 'go')
ax.add_line(plt.Polygon(grid['obstacle'], facecolor="grey"))
# plt.gca().set_aspect('equal')
# plt.xlim(-2,18)
# plt.ylim(-2,18)
blocked = obstacle(grid['obstacle'])

start = grid['path']['start']
target = grid['path']['target']


def update_front(front, position, target, path=None):
	new_front = []
	if not path:
		path = []
	for node in get_neighbours(position):
		if node in front or node in visited:
			continue
		estimate = h(node, target)
		new_front.append((node, estimate + len(path), path + [position]))
		if not node == start:
			ax.plot(node[0], node[1], 'bD', fillstyle='none')
	return new_front


def clear_front(front):
	nodes = {}
	for candidate in front:
		position = candidate[0]
		if position in nodes:
			if nodes[position][1] > candidate[1]:
				nodes[position] = candidate
		else:
			nodes[position] = candidate
	return [nodes[pos] for pos in nodes]


def distance_to_color(distance, size=25):
	cross = math.sqrt(2 * (size ** 2))
	return 1 - (distance / cross)


front = [(start, h(start, target), [start])]
visited = []
final_path = []
done = False


def animate(i):
	global front, final_path, done
	if i == 0 or done:
		return
	if len(final_path) > 0 and not done:
		ax.add_line(plt.Polygon(final_path, closed=False, fill=False, edgecolor="r"))
		done = True
		return
	# ax.plot(i/4, i/2, 'bo')
	min_step = min(list(zip(*front))[1])
	new_front = []
	for candidate in filter(lambda x: x[1] <= min_step, front):
		# print(f"{i:<3}", "expand:", candidate, min_step)
		node, distance, path = candidate
		if node[0] == target[0] and node[1] == target[1]:
			new_front = []
			front = []
			final_path = path + [target]
			ax.plot(node[0], node[1], 'rx')
			print("target reached!")
			print("path", candidate)
			break
		for entry in front:
			if node == entry[0]:
				front.remove(entry)
		visited.append(node)
		ax.plot(node[0], node[1], 's', color=(0, distance_to_color(h(node, target)), 0))
		new_front += update_front(front, node, target, path=path)
	front = clear_front(front + new_front)


anim = animation.FuncAnimation(fig, animate, interval=50, frames=130, repeat=False)
in_notebook = False

if in_notebook:
	from IPython.display import HTML
	HTML(anim.to_jshtml())
	plt.show()
else:
	anim.save("animation.mp4")
	with open("animation.html", "w") as out:
		out.write(anim.to_jshtml())
	plt.savefig("result.png")
