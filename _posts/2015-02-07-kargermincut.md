---
title: "全局最小割：Karger's Min Cut Algorithm"
date: 2015-02-07
categories: 
  - "algorithm"
tags: 
  - "最小割"
mathjax: true
---

<figure style="text-align: center;">
  <img src="/assets/images/kargers-algorithm-3.png" alt="Cut in an undirected graph" />
  <figcaption>Cut in an undirected graph</figcaption>
</figure>

提到无向图的最小割问题，首先想到的就是[Ford-Fulkerson算法](http://en.wikipedia.org/wiki/Ford%E2%80%93Fulkerson_algorithm)解s-t最小割，通过[Edmonds–Karp](http://en.wikipedia.org/wiki/Edmonds%E2%80%93Karp_algorithm)实现可以在$O(nm^2)$时间内解决这个问题（$n$为图中的顶点数，$m$为图中的边数）。

但是全局最小割和s-t最小割不同，并没有给定的指定的源点s和汇点t，如果通过Ford-Fulkerson算法来解这一问题，则需要枚举汇点t（共$n-1$），时间复杂度为$O\\left(n^2m^2\\right)$。

Can we do better?

<!--more-->

答案是肯定的，Karger在攻读博士学位期间（Orz...）提出了非常著名的基于随机化的全局最小割算法，算法非常简单，简单到不敢相信它是正确的，算法描述如下：

1. 在图中随机取一条边，将边的两个端点合并（contraction），同时消除所有由于合并而形成自环的边
<figure style="text-align: center;">
  <img src="/assets/images/kargers-algorithm-4.png" alt="Contraction" />
  <figcaption>Contraction</figcaption>
</figure>3. 重复步骤1直到图中仅剩下两个点
4. 将最终两点之间的边作为找的割返回

{% raw %}
这样一次运算的复杂度为$O(m)$，我们可以看到，这样随机的过程返回的结果是不确定的，找到的割并不一定是最小的，事实上可以证明，一次运行找到最小割的概率最低为$1/{{n}\\choose{2}}$，那么，将上述算法重复执行${{n}\\choose{2}}\\ln n$次，我们可以以低于的$1/n$的失败概率获得最小割，这就是Karger全局最小割算法的基本思想，时间复杂度为$O(n^2m\\ln n)$。（算法的证明很有意思，偷懒不写了哈哈，可以在参考资料中查到）
{% endraw %}

下面的C++实现仅仅是在我学习Karger算法的过程中为了理解算法而做的，因此效率很低，仅用来参考，为了简化实现，我通过暴力随机顶点对并检查的方法生成随机边，可以通过更有效的方法生成随机边来加速算法执行。

`#include #include #include #include #include #include #include #include  using namespace std;  class Graph { public: void addVertex() { _storage.push_back(list()); }  void addEdge(int vertex, int adjacent) { _storage[vertex].push_back(adjacent); }  int vertices() { return _storage.size(); }  int edges() { int count = 0; for (int i = 0; i < vertices(); ++i) { count += _storage[i].size(); } return count; }  bool isEdgeExist(int s, int t) { list &edges = _storage[s]; for (int adjacent : edges) { if (adjacent == t) { return true; } }  return false; }  list &edges_for_vertex(int vertex) { return _storage[vertex]; }  private: vector > _storage; };  class UnionFind { public: UnionFind(int size) { _storage.resize(size); for (int i = 0; i < size; ++i) { _storage[i] = i; } }  void UFUnion(int x, int y) { int root_x = UFFind(x); int root_y = UFFind(y);  if (root_x != root_y) { _storage[root_y] = root_x; } }  int UFFind(int x) { if (_storage[x] == x) { return x; }  int root = UFFind(_storage[x]); _storage[x] = root; // path compress return root; }  private: vector _storage; };  class MinCut { public: int kargerMinCut(Graph &graph) { int n = graph.vertices(); int m = graph.edges(); int t = n * n * (int)ceil(log(n));  cout << "Vertices : " << n << endl; cout << "Edges : " << m << endl; cout << "Repeat : " << t << endl;  int cut = INT_MAX;  // repeat n^2*ln(n) times for (int i = 0; i < t; ++i) { UnionFind ufset(n);  // after n-2 times contraction, there would be exactly 2 super vertices. for (int j = 0; j < n - 2; ++j) { // pick a random edge int x, y; do { x = rand() % n; y = rand() % n; } while (!(graph.isEdgeExist(x, y) && ufset.UFFind(x) != ufset.UFFind(y)));  // do the contraction ufset.UFUnion(x, y); }  cut = min(cut, countCut(graph, ufset)); }  return cut; }  private: int countCut(Graph &graph, UnionFind &ufset) { int count = 0; int n = graph.vertices();  for (int i = 0; i < n; ++i) { list &edges = graph.edges_for_vertex(i); for (int adjacent : edges) { if (ufset.UFFind(i) != ufset.UFFind(adjacent)) { count ++; } } }  assert(~(count & 1)); return count >> 1; } };  int main(int argc, char *argv[]) { ifstream fin("kargerMinCut.txt"); string line; stringstream stream;  Graph graph;  while (getline(fin, line)) { int vertex, adjacent;  stream.clear(); stream << line; stream >> vertex; graph.addVertex(); while (stream >> adjacent) { graph.addEdge(vertex - 1, adjacent - 1); } }  MinCut mincut; srand((unsigned)clock()); cout << mincut.kargerMinCut(graph) << endl;  return 0; }`

简单解释一下：对于边的contraction操作我使用并查集来模拟，非常类似于Kruskal算法的实现。

对于算法的执行过程还有一些更加高级的优化可以使得整个计算过程大大加速，不过这些优化超出了本文的范围，想了解的同学可以看[这里](http://www.cs.tau.ac.il/~zwick/grad-algo-08/gmc.pdf)，时间复杂度下降到了$O(n^2\\log ^3n)$。

使用的[测试数据](/assets/images/kargerMinCut.txt)

* * *

## 参考资料

- 《Algorithm Design》 Jon Kleinberg, Eva Tardos
- [Karger's Algorithm for Minimum Cuts](http://www.maillard.it/blog/kargers-algorithm/ "Karger's Algorithm for Minimum Cuts")
