ENTRY
 ↓
NormalizeInput
 ↓
IntentDetection (LLM-based)
 ↓
IntentConfidenceGate
 ├─ Low confidence → ClarificationNode
 └─ High confidence
        ↓
EntityExtraction (LLM-assisted)
 ↓
DomainValidation (tool-backed)
 ↓
IntentRouter
 ├─ ProcurementFlow
 │    ├─ CheckDomainAvailabilityTool
 │    ├─ ValidateBusinessContextTool
 │    ├─ CreateICARETicketTool
 │    └─ ProcurementResponseNode
 │
 ├─ DNSFlow
 │    ├─ ValidateDomainOwnershipTool
 │    ├─ LookupDNSProviderTool
 │    ├─ FetchDNSChangeFormTool
 │    └─ DNSResponseNode
 │
 ├─ TransferFlow
 │    ├─ ValidateTransferEligibilityTool
 │    ├─ IdentifyRegistrarTool
 │    ├─ CreateTransferRequestTool
 │    └─ TransferResponseNode
 │
 ├─ OwnershipFlow
 │    ├─ LookupDomainInDISTool
 │    ├─ FetchOwnerContactsTool
 │    └─ OwnershipResponseNode
 │
 ├─ URLRedirectFlow
 │    ├─ ValidateDomainTool
 │    ├─ IdentifyRedirectOwnerTool
 │    └─ RedirectResponseNode
 │
 ├─ SubdomainRejectFlow
 │    ├─ ExtractParentDomainTool
 │    ├─ LookupNameServersTool
 │    └─ SubdomainRejectionResponseNode
 │
 └─ GeneralInquiryFlow
      ├─ KnowledgeLookupTool
      └─ GeneralResponseNode
 ↓
ResponseFormatter
 ↓
END