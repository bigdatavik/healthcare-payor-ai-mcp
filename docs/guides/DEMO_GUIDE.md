# 🏥 Healthcare Payor AI System - Demo Guide

## Overview
This demo guide walks you through the Healthcare Payor AI System featuring **Unity Catalog Integration**. The system now seamlessly connects unstructured text documents (prior authorizations, customer service communications) with structured data from Unity Catalog tables.

## 🚀 Quick Start

### Prerequisites
- Databricks workspace with Unity Catalog configured
- Python environment with required dependencies
- Healthcare payor data loaded in `my_catalog.payer_silver` schema
- **⚠️ CRITICAL: Knowledge Assistant must be retrained with updated text documents using UC member IDs**

### Launch the Demo
```bash
./run_demo.sh
```

## 📋 Demo Menu Options

### 1. Check App Status
Verifies if the Streamlit application is running on `http://localhost:8503`

### 2. Start App
Launches the Healthcare Payor AI System using the MCP (Model Context Protocol) integration

### 3. Run Interactive Demo Script
Executes the automated demo script that showcases various AI agent capabilities

### 4. Open Browser to App
Opens your default browser to the running application

### 5. **NEW: Show Sample Test Questions (UC Integration)**
Displays comprehensive test questions that demonstrate the Unity Catalog integration capabilities

### 6. Show Demo Guide
Opens this demo guide

### 7. Exit
Closes the demo launcher

## 🔗 Unity Catalog Integration Features

### What's New
- **Direct Member ID Connectivity**: Text documents now use actual UC member IDs (1001, 1002, 1003)
- **Seamless Data Lookup**: AI agents can instantly query member demographics, plans, and claims
- **Complete Member Profiles**: Combines clinical scenarios with structured data
- **Cross-System Queries**: Links authorization requests with claims history and member details

### Member Data Mapping
| UC Member ID | Name | Plan | Claims | Text Document Usage |
|--------------|------|------|--------|-------------------|
| 1001 | John Doe | PLN101 | $120 paid | Preventive visit auth + billing issue + critical care |
| 1002 | Jane Smith | PLN102 | $200 denied | Gallbladder surgery + MRI coverage + knee pain |
| 1003 | Paul White | PLN101 | $300 paid | Denied knee surgery + surgery appeal |

## 🧪 Sample Test Questions

### 📋 Member Profile Questions
Test the AI agent's ability to retrieve and combine UC data with text documents:

**Basic Profile Lookup:**
```
"Tell me about member 1001 - what's their full profile?"
```
*Expected: Combines John Doe's UC demographics with prior auth and customer service history*

**Plan Information:**
```
"What is John Doe's plan type and when did it become effective?"
```
*Expected: PLN101, effective 2020-01-01, plus related coverage details*

**Demographics + Claims:**
```
"Show me member 1002's demographics and recent claims history"
```
*Expected: Jane Smith's profile with $200 denied claim details*

### 🔗 Cross-Reference Questions
Test the integration between different data sources:

**Billing + Authorization Correlation:**
```
"Member 1001 had a billing issue - what was their recent authorization about?"
```
*Expected: Links CS001 billing problem with PA001 preventive visit authorization*

**Claims + Prior Auth Analysis:**
```
"Why was member 1002's claim denied? Check their prior authorization status"
```
*Expected: Correlates denied claim with gallbladder surgery authorization*

**Appeal + UC Data:**
```
"Member 1003 appealed a surgery denial - what does their UC data show?"
```
*Expected: Connects surgery appeal email with member profile and claims*

### 💰 Claims & Authorization Correlation
Test financial data integration:

**Paid Claims Analysis:**
```
"Compare member 1001's paid claim with their approved prior authorization"
```
*Expected: Shows $120 paid claim matches approved preventive visit*

**Denial Pattern Analysis:**
```
"Member 1002 has a denied claim - what prior auth issues did they have?"
```
*Expected: Links $200 denied claim with authorization challenges*

**Complete Financial Picture:**
```
"Show me the complete financial picture for member 1003"
```
*Expected: $300 paid claim despite surgery denial, full financial timeline*

### 🏥 Clinical & Administrative Integration
Test healthcare-specific scenarios:

**Procedure Code Lookup:**
```
"Member 1001 called about CPT 99213 billing - check their plan coverage"
```
*Expected: Links billing issue with plan benefits and authorization*

**Surgery Status Check:**
```
"What's the status of member 1002's gallbladder surgery authorization and claims?"
```
*Expected: Complete surgery journey from auth to claim*

**Denial + Claims Correlation:**
```
"Member 1003's knee surgery was denied - do they have other paid claims?"
```
*Expected: Shows denied surgery but successful other claims*

### 📊 Analytics Questions
Test business intelligence capabilities:

**Cross-System Pattern Analysis:**
```
"Which members have both customer service issues and prior auth problems?"
```
*Expected: Identifies patterns across all three members*

**Plan Type Analysis:**
```
"Show me approval rates by member plan type (PLN101 vs PLN102)"
```
*Expected: Compares PLN101 vs PLN102 outcomes*

**Satisfaction Correlation:**
```
"What's the correlation between member satisfaction and claim status?"
```
*Expected: Links satisfaction scores with claim outcomes*

### 🎯 Business Intelligence
Test advanced analytics:

**High-Value Member Analysis:**
```
"Identify members with high-value claims and authorization patterns"
```
*Expected: Profiles members by claim amounts and authorization complexity*

**Plan Performance:**
```
"Which plan type (PLN101/PLN102) has more billing disputes?"
```
*Expected: Analyzes dispute patterns by plan type*

**Member Journey Mapping:**
```
"Show member journey from authorization to claim to customer service"
```
*Expected: Complete end-to-end member experience analysis*

## 🎬 Demo Workflow

### Step 1: Launch the System
1. Run `./run_demo.sh`
2. Select option **2** to start the app
3. Wait for "✅ App started successfully!" message

### Step 2: Access the Interface
1. Select option **4** to open browser
2. Navigate to `http://localhost:8503`
3. Familiarize yourself with the interface

### Step 3: Review Test Questions
1. In the demo launcher, select option **5**
2. Review the comprehensive test questions
3. Copy questions you want to test

### Step 4: Test UC Integration
1. In the web interface, paste test questions
2. Observe how the AI agent:
   - Queries UC tables for member data
   - Searches text documents for context
   - Combines both sources in responses
   - Provides comprehensive answers

### Step 5: Explore Advanced Features
1. Test cross-reference questions
2. Try analytics queries
3. Experiment with business intelligence scenarios

## 🔍 What to Look For

### Successful Integration Indicators
- ✅ AI agent retrieves UC member data (demographics, plans, claims)
- ✅ AI agent searches text documents for context
- ✅ Responses combine both structured and unstructured data
- ✅ Cross-references work seamlessly
- ✅ Member journeys are complete and accurate

### Advanced Capabilities
- 📊 Analytics across multiple data sources
- 🔗 Real-time cross-system queries
- 💡 Business intelligence insights
- 🎯 Predictive member behavior analysis
- 📈 Performance metrics and trends

## 🛠️ Troubleshooting

### Common Issues

**App Won't Start:**
- Check if port 8503 is available
- Verify all dependencies are installed
- Ensure Databricks credentials are configured

**UC Connection Issues:**
- Verify `config.py` has correct workspace hostname
- Check Unity Catalog permissions
- Ensure `my_catalog.payer_silver` schema exists

**Knowledge Assistant Training Issue:**
- The Knowledge Assistant endpoint (`ka-d0808962-endpoint`) was trained with original member IDs (M123456789, etc.)
- Text documents have been updated to use UC member IDs (1001, 1002, 1003)
- **Knowledge Assistant must be retrained with updated documents for integration to work**

**Missing Test Data:**
- Run the medallion ETL notebook to create base tables
- Execute the UC functions creation notebook
- Verify member IDs 1001, 1002, 1003 exist in UC tables
- **Upload updated .txt files to Unity Catalog volume and retrain Knowledge Assistant**

**Text Document Issues:**
- Ensure member IDs in text files match UC member IDs
- Check that all .txt files are in the `data/` directory
- Verify file permissions are correct

### Getting Help
1. Check the application logs in the terminal
2. Verify configuration in `config.py`
3. Test UC connection with `python mcp_uc_functions_client.py`
4. Review the README.md for setup instructions

## 🎯 Demo Success Criteria

By the end of this demo, you should be able to:
- [x] Launch the Healthcare Payor AI System
- [x] Ask questions that span both UC data and text documents
- [x] See complete member profiles combining all data sources
- [x] Understand the business value of integrated healthcare data
- [x] Demonstrate advanced analytics capabilities
- [x] Show real-time cross-system queries

## 📚 Additional Resources

- **Setup Guide**: `README.md`
- **Configuration**: `config.py`
- **UC Functions**: `notebooks/define_uc_tools_payor.ipynb`
- **Data Sources**: `data/` directory
- **MCP Integration**: `enhanced_healthcare_payor_app_mcp.py`

---

**🎉 Congratulations!** You now have a fully integrated Healthcare Payor AI System that seamlessly combines structured Unity Catalog data with unstructured text documents, enabling powerful analytics and comprehensive member insights.
