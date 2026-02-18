# AI Consulting/Fractional Services - Pricing & Packaging Research

**Research Date:** February 2026
**Compiled for:** Franco Schiavone

---

## 1. Market Rates for Fractional AI Engineers

### US Market Rates (Hourly)

| Experience Level | Hourly Rate Range | Annual Equivalent |
|-----------------|-------------------|-------------------|
| Junior (0-2 years) | $50-$80/hr | $100K-$160K |
| Mid-Level (2-5 years) | $80-$150/hr | $160K-$300K |
| Senior (5-10 years) | $150-$250/hr | $300K-$500K |
| Principal/Staff (10+ years) | $200-$400/hr | $400K-$800K |
| Fractional CTO/AI Lead | $250-$500/hr | $500K-$1M+ |

**Sources:**
- Coursera ML Engineer Salary Guide 2025: $116K-$140K base salary
- PayScale Data Scientist Salary: $59K-$156K/year
- Glassdoor ML Engineer: $98K (entry) to $167K (15+ years)
- Senior ML Engineer: $131K-$177K base

### Freelance/Contract Premium
- **Contractors typically charge 1.5-2x the hourly equivalent of salaried roles**
- Reason: No benefits, self-employment tax, downtime between projects
- Premium specialists (LLMs, RAG, Computer Vision): Additional 20-50%

### Regional Rate Differences

| Region | Rate vs US | Typical Range |
|--------|-----------|---------------|
| US (SF/NYC) | 100% (baseline) | $150-$400/hr |
| US (Other) | 80-90% | $120-$300/hr |
| Western Europe | 70-85% | $100-$250/hr |
| Eastern Europe | 40-60% | $60-$150/hr |
| Latin America | 30-50% | $45-$120/hr |
| India/SE Asia | 20-40% | $30-$80/hr |

### LATAM-Specific Context
- Argentina: $40-$100/hr for senior AI engineers
- Brazil: $50-$120/hr for senior roles
- Mexico: $45-$110/hr
- **Premium for US-facing, English-fluent talent: +20-30%**

---

## 2. Document Intelligence/Processing as a Service

### Platform Pricing Benchmarks

**LlamaCloud (LlamaIndex) - Document Ingestion Platform:**
| Plan | Price | Included Credits | Users |
|------|-------|------------------|-------|
| Free | $0 | 10K credits | 1 |
| Starter | $50/mo base | 40K credits | 5 |
| Pro | $500/mo | 400K credits | 10 |
| Enterprise | Custom | Volume discounts | Unlimited |

- **Credit cost: 1,000 credits = $1.25**
- Basic parsing: ~1 credit/page
- Layout-aware agentic parsing: Higher cost for accuracy

**LangSmith (LangChain) - Agent Development Platform:**
| Plan | Price | Traces | Features |
|------|-------|--------|----------|
| Developer | Free | 5K/month | 1 seat |
| Plus | $39/seat/mo | 10K included | Unlimited seats |
| Enterprise | Custom | Custom | SSO, SLA, dedicated support |

- **Extended traces (400-day retention): $5/1K traces**

### Document Intelligence Service Pricing Models

| Service Type | Typical Pricing |
|-------------|-----------------|
| **Per-document processing** | $0.05-$0.50/doc (simple) to $1-$5/doc (complex) |
| **Per-page OCR/extraction** | $0.01-$0.10/page |
| **Monthly retainer** | $2K-$10K/mo for ongoing processing |
| **Project-based** | $5K-$50K for custom pipeline setup |
| **RAG implementation** | $10K-$100K+ depending on complexity |

### RAG Implementation Cost Breakdown

| Component | Typical Cost |
|-----------|-------------|
| Discovery/Assessment | $2K-$10K |
| Data pipeline setup | $5K-$25K |
| Vector database setup | $2K-$10K |
| LLM integration | $5K-$20K |
| Testing & optimization | $3K-$15K |
| Documentation & training | $2K-$8K |
| **Total project** | $20K-$100K+ |

---

## 3. Productized AI Services Examples

### Brett Kromkamp (Contextualise AI)
- **Model:** Platform + consulting
- **Focus:** Knowledge graphs, data integration, AI workflows
- **Target:** Organizations needing complex data management
- **Services:** Data pipeline design, graph modeling, AI integration

### Common AI Agency Pricing Models

**Retainer Model:**
| Tier | Monthly Fee | Typical Deliverables |
|------|-------------|---------------------|
| Light | $2K-$5K | 10-20 hrs, maintenance, light support |
| Standard | $5K-$15K | 20-40 hrs, ongoing development, support |
| Premium | $15K-$50K | 40-80 hrs, dedicated team, priority |

**Project/Sprint Model:**
| Sprint Type | Duration | Price Range |
|-------------|----------|-------------|
| Discovery Sprint | 1-2 weeks | $5K-$15K |
| MVP Sprint | 4-6 weeks | $15K-$50K |
| Implementation Sprint | 6-12 weeks | $50K-$150K |

### Productized Service Examples

| Service | Typical Pricing |
|---------|-----------------|
| **AI Chatbot implementation** | $5K-$25K + $500-$2K/mo maintenance |
| **Document processing pipeline** | $10K-$40K + usage fees |
| **Custom RAG system** | $20K-$80K |
| **AI integration audit** | $3K-$10K |
| **AI strategy workshop** | $2K-$8K (1-2 days) |

---

## 4. Sprint Product Structure for AI Services

### Recommended Sprint Model

#### **Discovery Sprint (1-2 weeks, $5K-$15K)**

**Deliverables:**
- [ ] Technical assessment document
- [ ] Data audit and quality report
- [ ] AI opportunity mapping
- [ ] Proof-of-concept for highest-value use case
- [ ] Implementation roadmap with estimates
- [ ] Go/no-go recommendation

**Input from client:**
- Access to relevant data/systems
- 2-3 stakeholder interviews
- Clear problem statement

---

#### **MVP Sprint (4-6 weeks, $15K-$50K)**

**Deliverables:**
- [ ] Working prototype of core AI feature
- [ ] Basic evaluation metrics
- [ ] Documentation (technical + user)
- [ ] Deployment to staging environment
- [ ] Handoff/training session
- [ ] 30-day support period

**Prerequisites:**
- Completed Discovery Sprint or equivalent
- Data access secured
- Success criteria defined

---

#### **Production Sprint (6-12 weeks, $50K-$150K)**

**Deliverables:**
- [ ] Production-ready AI system
- [ ] Full test suite (unit, integration, eval)
- [ ] Monitoring and alerting setup
- [ ] CI/CD pipeline
- [ ] Security review
- [ ] Performance optimization
- [ ] Comprehensive documentation
- [ ] Team training (2-4 sessions)
- [ ] 90-day support + SLA

---

### Sprint Pricing Factors

| Factor | Price Impact |
|--------|--------------|
| Data complexity | +20-50% |
| Integration requirements | +15-30% |
| Real-time requirements | +25-40% |
| Compliance (HIPAA, SOC2) | +20-35% |
| Multi-language support | +15-25% |
| Urgent timeline (< normal) | +30-50% |

---

## 5. Document Intelligence Service Templates

### Template A: Document Processing Pipeline

**Package Name:** DocIntel Essentials

**Scope:**
- Process up to 10 document types
- Extract up to 50 fields per document
- Basic validation and quality checks
- API integration

**Pricing:**
- Setup: $15K-$30K
- Monthly: $1K-$3K (includes 10K docs/month)
- Overage: $0.05-$0.15/doc

**Timeline:** 4-8 weeks

---

### Template B: RAG Knowledge Base

**Package Name:** KnowledgeRAG Pro

**Scope:**
- Ingest up to 10,000 documents
- Custom chunking strategy
- Hybrid search (vector + keyword)
- Source attribution
- Chat interface

**Pricing:**
- Setup: $25K-$60K
- Monthly: $2K-$5K (hosting + maintenance)
- Custom integrations: $5K-$15K each

**Timeline:** 6-10 weeks

---

### Template C: End-to-End Document Intelligence

**Package Name:** Enterprise DocAI

**Scope:**
- Unlimited document types (within reason)
- Custom extraction models
- Workflow automation
- Human-in-the-loop review
- Analytics dashboard
- SSO/SAML integration

**Pricing:**
- Discovery: $10K-$20K
- Implementation: $50K-$150K
- Annual: $24K-$60K (support + evolution)

**Timeline:** 8-16 weeks

---

## 6. Recommended Packaging for Franco

### Suggested Service Tiers

#### **Fractional AI Engineer**

| Commitment | Hours/Month | Monthly Rate | Effective Hourly |
|------------|-------------|--------------|------------------|
| Light | 20 hrs | $3K-$4K | $150-$200 |
| Standard | 40 hrs | $5K-$7K | $125-$175 |
| Half-time | 80 hrs | $9K-$12K | $112-$150 |
| Full-time | 160 hrs | $16K-$22K | $100-$137 |

*Note: Lower effective hourly for higher commitment = predictable income*

---

#### **Document Intelligence Sprint**

| Sprint | Duration | Price | Ideal For |
|--------|----------|-------|-----------|
| **Assessment** | 1 week | $3K-$5K | Feasibility check |
| **Quick Win** | 2-3 weeks | $8K-$15K | Single doc type, simple extraction |
| **Standard** | 4-6 weeks | $20K-$40K | Multi-doc, moderate complexity |
| **Enterprise** | 8-12 weeks | $50K-$100K | Complex, integrations, compliance |

---

### Value-Based Pricing Considerations

| If client saves/gains... | Consider charging... |
|--------------------------|---------------------|
| $100K+/year in labor | $20K-$40K (20-40% of value) |
| $500K+/year in efficiency | $75K-$150K |
| $1M+/year in new revenue | $150K-$300K |

---

## 7. Key Takeaways & Recommendations

### Pricing Strategy
1. **Start higher than comfortable** - AI expertise commands premium
2. **Offer value-based pricing** when ROI is clear
3. **Create packages** to reduce custom quoting overhead
4. **Include maintenance** in project pricing (10-20% of build cost annually)

### Positioning
1. **Specialize** in document intelligence/RAG - narrow focus = higher rates
2. **Showcase case studies** with concrete metrics
3. **Productize** common requests into standard offerings
4. **Build assets** (templates, frameworks) that accelerate delivery

### Rate Validation (2024-2025 Market)
- Senior AI engineers: $150-$300/hr is defensible
- RAG/LLM specialists: $200-$400/hr in hot markets
- LATAM-based with US clients: $80-$180/hr range is competitive
- Fractional arrangements: Premium over full-time rate equivalent

---

## Sources

1. Coursera - Machine Learning Engineer Salary Guide (2025)
2. PayScale - Data Scientist Salary Data
3. Glassdoor - ML Engineer Salary Data
4. LlamaCloud Pricing Page (2026)
5. LangSmith Pricing Page (2026)
6. Kalzumeus - "Don't Call Yourself a Programmer" (Patrick McKenzie)
7. Industry knowledge and market research

---

*Note: Some sources were inaccessible due to API restrictions. Rates are based on successfully retrieved data and industry knowledge. Recommend validating with current market research before finalizing pricing.*
