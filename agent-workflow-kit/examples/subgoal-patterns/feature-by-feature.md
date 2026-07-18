# Feature-by-Feature Subgoal Pattern

## When to Use

Use this pattern when building multiple independent features that can be developed in parallel.

## Pattern

Split work by independent features, with each subagent handling one complete feature end-to-end.

## Example: Building an E-commerce Dashboard

### Subgoal 1: Sales Overview Feature
```
Implement sales overview dashboard with charts and metrics.
Context: Building e-commerce admin dashboard. This is one of several dashboard features.
Deliverable: Sales overview component, API endpoints for sales data, chart integration.
Boundaries: Do not touch other dashboard features (inventory, customers, etc.). Focus only on sales.
Verification: Component renders correctly, API returns correct sales data, charts display properly.
Return: summary · component code · API endpoints · test results · performance metrics.
```

### Subgoal 2: Inventory Management Feature
```
Implement inventory management interface with stock tracking.
Context: Building e-commerce admin dashboard. This is independent of sales overview.
Deliverable: Inventory list component, stock update endpoints, low-stock alerts.
Boundaries: Do not touch sales or customer features. Focus only on inventory.
Verification: Inventory updates work correctly, alerts trigger at thresholds, UI is responsive.
Return: summary · component code · API endpoints · test results · alert configuration.
```

### Subgoal 3: Customer Management Feature
```
Implement customer management interface with search and filtering.
Context: Building e-commerce admin dashboard. This is independent of other features.
Deliverable: Customer list component, search/filter logic, customer detail view.
Boundaries: Do not touch sales or inventory features. Focus only on customers.
Verification: Search returns correct results, filters work, customer details load properly.
Return: summary · component code · search logic · test results · performance metrics.
```

### Subgoal 4: Integration & Layout
```
Integrate all dashboard features into main layout with navigation.
Context: All three features are complete from Subgoals 1-3.
Deliverable: Main dashboard layout, navigation menu, responsive design.
Boundaries: Do not modify feature implementations. Focus on layout and navigation.
Verification: All features accessible via navigation, layout works on all screen sizes.
Return: summary · layout code · navigation implementation · responsive test results.
```

## Synthesis

After all subgoals complete:
1. Verify all features work independently
2. Test navigation between features
3. Check for shared state conflicts
4. Review consistent UI/UX across features
5. Test performance with all features loaded

## Benefits

- True parallel development of independent features
- Each feature is complete end-to-end
- Easy to prioritize or defer features
- Clear ownership per feature

## Considerations

- Ensure features are truly independent
- Watch for shared state or dependencies
- Coordinate on shared UI components
- Plan integration testing carefully
