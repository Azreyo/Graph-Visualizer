#include <iostream>
#include <vector>
#include <queue>
#include <limits>
#include <algorithm>
#include <cstring>
#include <set>
#include <map>
#include <stack>
#include <cmath>

using namespace std;

const int INF = numeric_limits<int>::max();


class UnionFind {
public:
    vector<int> parent, rank_;
    
    UnionFind(int n) : parent(n), rank_(n, 0) {
        for (int i = 0; i < n; i++) parent[i] = i;
    }
    
    int find(int x) {
        if (parent[x] != x) parent[x] = find(parent[x]);
        return parent[x];
    }
    
    bool unite(int x, int y) {
        int px = find(x), py = find(y);
        if (px == py) return false;
        if (rank_[px] < rank_[py]) swap(px, py);
        parent[py] = px;
        if (rank_[px] == rank_[py]) rank_[px]++;
        return true;
    }
};

struct Edge {
    int u, v, weight;
    bool operator<(const Edge& other) const {
        return weight < other.weight;
    }
};


vector<int> dijkstra(int start, int end, int n, const vector<vector<pair<int,int>>>& adj, int& dist) {
    vector<int> d(n, INF), parent(n, -1);
    priority_queue<pair<int,int>, vector<pair<int,int>>, greater<>> pq;
    
    d[start] = 0;
    pq.push({0, start});
    
    while (!pq.empty()) {
        auto [du, u] = pq.top(); pq.pop();
        if (du > d[u]) continue;
        
        for (auto [v, w] : adj[u]) {
            if (d[u] + w < d[v]) {
                d[v] = d[u] + w;
                parent[v] = u;
                pq.push({d[v], v});
            }
        }
    }
    
    dist = d[end];
    vector<int> path;
    if (d[end] != INF) {
        for (int v = end; v != -1; v = parent[v]) path.push_back(v);
        reverse(path.begin(), path.end());
    }
    return path;
}


vector<vector<int>> floydWarshall(int n, const vector<Edge>& edges) {
    vector<vector<int>> dist(n, vector<int>(n, INF));
    
    for (int i = 0; i < n; i++) dist[i][i] = 0;
    
    for (const auto& e : edges) {
        dist[e.u][e.v] = min(dist[e.u][e.v], e.weight);
        dist[e.v][e.u] = min(dist[e.v][e.u], e.weight);
    }
    
    for (int k = 0; k < n; k++) {
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                if (dist[i][k] != INF && dist[k][j] != INF) {
                    dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j]);
                }
            }
        }
    }
    return dist;
}


pair<int, vector<pair<int,int>>> kruskalMST(int n, vector<Edge> edges) {
    sort(edges.begin(), edges.end());
    UnionFind uf(n);
    
    int totalWeight = 0;
    vector<pair<int,int>> mstEdges;
    
    for (const auto& e : edges) {
        if (uf.unite(e.u, e.v)) {
            totalWeight += e.weight;
            mstEdges.push_back({e.u, e.v});
            if ((int)mstEdges.size() == n - 1) break;
        }
    }
    
    return {totalWeight, mstEdges};
}


pair<int, vector<pair<int,int>>> kruskalMaxST(int n, vector<Edge> edges) {
    sort(edges.begin(), edges.end(), [](const Edge& a, const Edge& b) {
        return a.weight > b.weight;
    });
    UnionFind uf(n);
    
    int totalWeight = 0;
    vector<pair<int,int>> mstEdges;
    
    for (const auto& e : edges) {
        if (uf.unite(e.u, e.v)) {
            totalWeight += e.weight;
            mstEdges.push_back({e.u, e.v});
            if ((int)mstEdges.size() == n - 1) break;
        }
    }
    
    return {totalWeight, mstEdges};
}


vector<int> findOddDegreeVertices(int n, const vector<Edge>& edges) {
    vector<int> degree(n, 0);
    for (const auto& e : edges) {
        degree[e.u]++;
        degree[e.v]++;
    }
    
    vector<int> oddVertices;
    for (int i = 0; i < n; i++) {
        if (degree[i] % 2 == 1) {
            oddVertices.push_back(i);
        }
    }
    return oddVertices;
}


int minWeightMatching(const vector<int>& oddVertices, const vector<vector<int>>& dist, vector<pair<int,int>>& matching) {
    int k = oddVertices.size();
    if (k == 0) return 0;
    if (k == 2) {
        matching.push_back({oddVertices[0], oddVertices[1]});
        return dist[oddVertices[0]][oddVertices[1]];
    }
    
    
    
    vector<int> dp(1 << k, INF);
    vector<int> parent(1 << k, -1);
    dp[0] = 0;
    
    for (int mask = 0; mask < (1 << k); mask++) {
        if (dp[mask] == INF) continue;
        
        
        int first = -1;
        for (int i = 0; i < k; i++) {
            if (!(mask & (1 << i))) {
                first = i;
                break;
            }
        }
        if (first == -1) continue;
        
        
        for (int second = first + 1; second < k; second++) {
            if (mask & (1 << second)) continue;
            
            int newMask = mask | (1 << first) | (1 << second);
            int cost = dist[oddVertices[first]][oddVertices[second]];
            
            if (dp[mask] + cost < dp[newMask]) {
                dp[newMask] = dp[mask] + cost;
                parent[newMask] = mask;
            }
        }
    }
    
    
    int fullMask = (1 << k) - 1;
    int curMask = fullMask;
    while (curMask != 0 && parent[curMask] != -1) {
        int prevMask = parent[curMask];
        int diff = curMask ^ prevMask;
        
        int first = -1, second = -1;
        for (int i = 0; i < k; i++) {
            if (diff & (1 << i)) {
                if (first == -1) first = i;
                else second = i;
            }
        }
        if (first != -1 && second != -1) {
            matching.push_back({oddVertices[first], oddVertices[second]});
        }
        curMask = prevMask;
    }
    
    return dp[fullMask];
}


vector<int> findEulerianCircuit(int n, vector<multiset<pair<int,int>>>& adjList) {
    
    int start = -1;
    for (int i = 0; i < n; i++) {
        if (!adjList[i].empty()) {
            start = i;
            break;
        }
    }
    if (start == -1) return {};
    
    vector<int> circuit;
    stack<int> stk;
    stk.push(start);
    
    while (!stk.empty()) {
        int u = stk.top();
        if (adjList[u].empty()) {
            circuit.push_back(u);
            stk.pop();
        } else {
            int v = adjList[u].begin()->second;
            
            adjList[u].erase(adjList[u].begin());
            
            for (auto it = adjList[v].begin(); it != adjList[v].end(); ++it) {
                if (it->second == u) {
                    adjList[v].erase(it);
                    break;
                }
            }
            stk.push(v);
        }
    }
    
    reverse(circuit.begin(), circuit.end());
    return circuit;
}


vector<int> reconstructPath(int u, int v, const vector<vector<int>>& dist, const vector<Edge>& edges, int n) {
    if (u == v) return {u};
    if (dist[u][v] == INF) return {};
    
    
    vector<int> parent(n, -1);
    vector<int> d(n, INF);
    queue<int> q;
    q.push(u);
    d[u] = 0;
    
    
    vector<vector<pair<int,int>>> adj(n);
    for (const auto& e : edges) {
        adj[e.u].push_back({e.v, e.weight});
        adj[e.v].push_back({e.u, e.weight});
    }
    
    
    priority_queue<pair<int,int>, vector<pair<int,int>>, greater<>> pq;
    pq.push({0, u});
    
    while (!pq.empty()) {
        auto [du, curr] = pq.top();
        pq.pop();
        if (du > d[curr]) continue;
        if (curr == v) break;
        
        for (auto [next, w] : adj[curr]) {
            if (d[curr] + w < d[next]) {
                d[next] = d[curr] + w;
                parent[next] = curr;
                pq.push({d[next], next});
            }
        }
    }
    
    vector<int> path;
    for (int curr = v; curr != -1; curr = parent[curr]) {
        path.push_back(curr);
    }
    reverse(path.begin(), path.end());
    return path;
}

pair<int, vector<int>> chinesePostman(int n, const vector<Edge>& edges) {
    if (edges.empty()) return {0, {}};
    
    int baseCost = 0;
    for (const auto& e : edges) {
        baseCost += e.weight;
    }
    
    vector<int> oddVertices = findOddDegreeVertices(n, edges);
    
    
    vector<multiset<pair<int,int>>> adjList(n);
    for (const auto& e : edges) {
        adjList[e.u].insert({e.weight, e.v});
        adjList[e.v].insert({e.weight, e.u});
    }
    
    int matchingCost = 0;
    
    if (!oddVertices.empty()) {
        auto dist = floydWarshall(n, edges);
        vector<pair<int,int>> matching;
        matchingCost = minWeightMatching(oddVertices, dist, matching);
        
        
        for (auto& [u, v] : matching) {
            vector<int> path = reconstructPath(u, v, dist, edges, n);
            
            for (size_t i = 0; i + 1 < path.size(); i++) {
                int a = path[i], b = path[i+1];
                
                int w = 0;
                for (const auto& e : edges) {
                    if ((e.u == a && e.v == b) || (e.u == b && e.v == a)) {
                        w = e.weight;
                        break;
                    }
                }
                adjList[a].insert({w, b});
                adjList[b].insert({w, a});
            }
        }
    }
    
    int totalCost = baseCost + matchingCost;
    
    vector<int> circuit = findEulerianCircuit(n, adjList);
    
    return {totalCost, circuit};
}



pair<int, vector<int>> tsp(int n, const vector<vector<int>>& dist, int start) {
    if (n == 1) return {0, {start}};
    if (n > 20) {
        
        vector<bool> visited(n, false);
        vector<int> path;
        int current = start;
        int totalDist = 0;
        
        path.push_back(current);
        visited[current] = true;
        
        for (int i = 1; i < n; i++) {
            int nearest = -1;
            int nearestDist = INF;
            for (int j = 0; j < n; j++) {
                if (!visited[j] && dist[current][j] < nearestDist) {
                    nearest = j;
                    nearestDist = dist[current][j];
                }
            }
            if (nearest == -1) break;
            
            visited[nearest] = true;
            path.push_back(nearest);
            totalDist += nearestDist;
            current = nearest;
        }
        
        
        totalDist += dist[current][start];
        path.push_back(start);
        
        return {totalDist, path};
    }
    
    
    vector<vector<int>> dp(1 << n, vector<int>(n, INF));
    vector<vector<int>> parent(1 << n, vector<int>(n, -1));
    
    dp[1 << start][start] = 0;
    
    for (int mask = 0; mask < (1 << n); mask++) {
        for (int u = 0; u < n; u++) {
            if (!(mask & (1 << u)) || dp[mask][u] == INF) continue;
            
            for (int v = 0; v < n; v++) {
                if (mask & (1 << v)) continue;
                if (dist[u][v] == INF) continue;
                
                int newMask = mask | (1 << v);
                if (dp[mask][u] + dist[u][v] < dp[newMask][v]) {
                    dp[newMask][v] = dp[mask][u] + dist[u][v];
                    parent[newMask][v] = u;
                }
            }
        }
    }
    
    int fullMask = (1 << n) - 1;
    int minDist = INF;
    int lastNode = -1;
    
    for (int u = 0; u < n; u++) {
        if (u == start) continue;
        if (dp[fullMask][u] != INF && dist[u][start] != INF) {
            if (dp[fullMask][u] + dist[u][start] < minDist) {
                minDist = dp[fullMask][u] + dist[u][start];
                lastNode = u;
            }
        }
    }
    
    if (minDist == INF) return {-1, {}};
    
    
    vector<int> path;
    int mask = fullMask;
    int cur = lastNode;
    
    while (cur != -1) {
        path.push_back(cur);
        int prev = parent[mask][cur];
        mask ^= (1 << cur);
        cur = prev;
    }
    
    reverse(path.begin(), path.end());
    path.push_back(start);  
    
    return {minDist, path};
}

int main() {
    string mode;
    cin >> mode;
    
    int n, m;
    cin >> n >> m;
    
    vector<Edge> edges(m);
    vector<vector<pair<int,int>>> adj(n);
    
    for (int i = 0; i < m; i++) {
        cin >> edges[i].u >> edges[i].v >> edges[i].weight;
        adj[edges[i].u].push_back({edges[i].v, edges[i].weight});
        adj[edges[i].v].push_back({edges[i].u, edges[i].weight});
    }
    
    if (mode == "dijkstra") {
        int start, end;
        cin >> start >> end;
        
        int dist;
        vector<int> path = dijkstra(start, end, n, adj, dist);
        
        if (path.empty()) {
            cout << "NO_PATH" << endl;
        } else {
            for (size_t i = 0; i < path.size(); i++) {
                cout << path[i];
                if (i < path.size() - 1) cout << " ";
            }
            cout << endl;
        }
    }
    else if (mode == "mst") {
        auto [weight, mstEdges] = kruskalMST(n, edges);
        
        cout << weight << endl;
        for (auto& e : mstEdges) {
            cout << e.first << " " << e.second << endl;
        }
    }
    else if (mode == "maxst") {
        auto [weight, mstEdges] = kruskalMaxST(n, edges);
        
        cout << weight << endl;
        for (auto& e : mstEdges) {
            cout << e.first << " " << e.second << endl;
        }
    }
    else if (mode == "chinese") {
        auto [cost, circuit] = chinesePostman(n, edges);
        
        cout << cost << endl;
        
        for (size_t i = 0; i < circuit.size(); i++) {
            cout << circuit[i];
            if (i < circuit.size() - 1) cout << " ";
        }
        cout << endl;
    }
    else if (mode == "tsp") {
        int start;
        cin >> start;
        
        auto dist = floydWarshall(n, edges);
        auto [cost, path] = tsp(n, dist, start);
        
        if (cost == -1) {
            cout << "NO_PATH" << endl;
        } else {
            cout << cost << endl;
            for (size_t i = 0; i < path.size(); i++) {
                cout << path[i];
                if (i < path.size() - 1) cout << " ";
            }
            cout << endl;
        }
    }
    
    return 0;
}
