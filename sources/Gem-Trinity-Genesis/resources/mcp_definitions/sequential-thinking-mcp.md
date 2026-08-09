# Sequential Thinking MCP Usage Rules

A server for dynamic and reflective problem-solving through structured thinking.

## Features

- Break down complex problems into manageable steps
- Revise and refine thoughts as understanding deepens
- Branch into alternative reasoning paths
- Adjust total number of thoughts dynamically
- Generate and verify solution hypotheses

## Available Tools

| Tool | Description |
|------|-------------|
| `sequential_thinking` | Structured step-by-step thinking process |

## Tool Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `thought` | string | ✅ | Current thinking step |
| `nextThoughtNeeded` | boolean | ✅ | Whether another step is needed |
| `thoughtNumber` | integer | ✅ | Current thought number |
| `totalThoughts` | integer | ✅ | Estimated total thoughts needed |
| `isRevision` | boolean | ❌ | Whether this revises previous thinking |
| `revisesThought` | integer | ❌ | Which thought is being reconsidered |
| `branchFromThought` | integer | ❌ | Branching point thought number |
| `branchId` | string | ❌ | Branch identifier |
| `needsMoreThoughts` | boolean | ❌ | If more thoughts are needed |

## When to Use

**Trigger:** Complex problem-solving, multi-step analysis, or decision-making tasks.

**Action:**
- Use for **complex debugging** requiring systematic analysis
- Use for **architectural decisions** with multiple trade-offs
- Use for **research tasks** requiring deep exploration
- Use when you need to **backtrack and revise** earlier conclusions

## Thinking Pattern

```
1. Initial thought → Assess problem scope
2. thought(1/5) → Break down components
3. thought(2/5) → Analyze first component
4. thought(3/5) → Discover issue, set isRevision=true
5. thought(4/5) → Branch with branchId for alternative
6. thought(5/5) → Synthesize conclusions
```

## Best Practices

1. **Start with estimate** - Set `totalThoughts` based on complexity
2. **Use revisions** - Don't hesitate to revise earlier thoughts
3. **Branch when needed** - Explore alternatives without losing main path
4. **Adjust dynamically** - Use `needsMoreThoughts` if underestimated
5. **Conclude explicitly** - Set `nextThoughtNeeded: false` to finish
