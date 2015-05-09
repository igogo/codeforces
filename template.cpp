#include <bits/stdc++.h>

// ############ TASK $$PROBLEM_LETTER$$ ##################

using namespace std;

typedef vector<int> vi;
typedef vector<string> vs;
typedef pair<int, int> pii;
typedef long long ll;

#define FV(i,v) for(int i=0; i<(int)(v).size(); i++)
#define FI(i,v) for(typeof(v.begin()) i = v.begin(); i != v.end(); ++i)
#define sz(v) (int)(v).size()
#define all(v) (v).begin(), (v).end()
#define REP(i,n) for(int (i) = 0; (i) < (n); (i)++)
#define FOR(i, st, en) for(int i=(st); i<(int)(en); i++)
#define CR(value) { cout << value << endl; return; }
#define RV(v) FV(i,v) cin >> v[i];
#define DRV(v, n) vi (v)(n); RV((v));

ll modulo(ll x, ll y) {
    return ((x % y) + y) % y;
}

void solve() {
}



#ifdef ONLINE_JUDGE
int main() { ios_base::sync_with_stdio(0); solve(); return 0; }
#else
void perform_testing(void (*solve)(), string problem, int itest);
int main() { perform_testing(solve, "$$PROBLEM_LETTER$$", -1); return 0; }
#endif // ONLINE_JUDGE
