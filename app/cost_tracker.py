import streamlit as st
from streamlit import session_state as ss


class CostTracker:
    def __init__(self):
        if 'cost_state' not in ss:
            ss.cost_state = {
                'estimated': 0.0,
                'actual': 0.0,
                'budget': 5.0,
                'history': [],
            }

    def estimate(self, tokens: int, price_per_1k: float) -> float:
        estimate = (tokens / 1000.0) * price_per_1k
        ss.cost_state['estimated'] = estimate
        ss.cost_state['history'].append({"type": "estimate", "value": estimate})
        return estimate

    def add_usage(self, value: float):
        ss.cost_state['actual'] += value
        ss.cost_state['history'].append({"type": "usage", "value": value})

    def remaining(self) -> float:
        return max(ss.cost_state.get('budget', 0) - ss.cost_state.get('actual', 0), 0)


class PageCostDashboard:
    def __init__(self):
        self.name = "Cost"
        self.tracker = CostTracker()

    def draw(self):
        st.subheader("Cost & Budget")
        st.caption("Track estimates, live usage, and budgets per run.")

        with st.expander("Estimation", expanded=True):
            tokens = st.number_input("Planned tokens", min_value=0, value=2000)
            price = st.number_input("$/1k tokens", min_value=0.0, value=0.004, step=0.001, format="%.3f")
            if st.button("Estimate cost"):
                estimate = self.tracker.estimate(tokens, price)
                st.success(f"Estimated ${estimate:.4f}")

        with st.expander("Live tracking", expanded=True):
            usage = st.number_input("Add usage ($)", min_value=0.0, value=0.1, step=0.01)
            if st.button("Record usage"):
                self.tracker.add_usage(usage)
            st.metric("Actual spend", f"${ss.cost_state['actual']:.2f}")
            st.metric("Budget", f"${ss.cost_state['budget']:.2f}")
            st.metric("Remaining", f"${self.tracker.remaining():.2f}")

        with st.expander("History"):
            st.json(ss.cost_state.get('history', []))
