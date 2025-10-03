# 🧪 Quick Test Questions Reference Card

## Unity Catalog Integration Test Questions

### 🚀 Quick Start Tests
Copy and paste these into the AI agent chat:

```
Tell me about member 1001 - what's their full profile?
```

```
Member 1001 had a billing issue - what was their recent authorization about?
```

```
Why was member 1002's claim denied? Check their prior authorization status
```

### 💡 Advanced Integration Tests

```
Which members have both customer service issues and prior auth problems?
```

```
Show member journey from authorization to claim to customer service
```

```
Compare member 1001's paid claim with their approved prior authorization
```

### 📊 Business Intelligence Tests

```
Show me approval rates by member plan type (PLN101 vs PLN102)
```

```
What's the correlation between member satisfaction and claim status?
```

```
Identify members with high-value claims and authorization patterns
```

## Expected Behaviors

✅ **UC Data Integration**: Agent retrieves member demographics, plans, claims
✅ **Text Document Search**: Agent finds relevant prior auths and customer service records  
✅ **Cross-Reference**: Agent connects data across all sources
✅ **Complete Profiles**: Agent provides comprehensive member insights
✅ **Real-time Analytics**: Agent performs calculations across integrated data

## Member Quick Reference

| ID | Name | Plan | Claim | Text Documents |
|----|------|------|-------|----------------|
| 1001 | John Doe | PLN101 | $120 paid | Preventive visit + billing issue |
| 1002 | Jane Smith | PLN102 | $200 denied | Surgery auth + MRI issue |
| 1003 | Paul White | PLN101 | $300 paid | Denied surgery + appeal |

---
*Use ./run_demo.sh option 5 for complete test question list*
