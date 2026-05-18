---
config:
  layout: elk
  elk:
    mergeEdges: false
    nodePlacementStrategy: NETWORK_SIMPLEX
    cycleBreakingStrategy: DEPTH_FIRST
    edgeRouting: ORTHOGONAL
  theme: forest
---
flowchart TB

%% =========================
%% ENTRYPOINT
%% =========================
subgraph EntryPoint["Entrypoint"]
    Main["main.py"]
end

%% =========================
%% COMPOSITION ROOT
%% =========================
subgraph CompositionRoot["Composition Root"]
    Dependencies["Dependencies"]
    Config["LakehouseConfig"]
end

%% =========================
%% DATA ACCESS
%% =========================
subgraph DataAccess["Data Access"]
    BefolkningRepo["BefolkningRepository"]
    LonnRepo["LonnSysselsettingRepository"]

    BefolkningDS["BefolkningDataSource"]
    LonnDS["LonnSysselsettingDataSource"]

    SSBBase["SSBDataSource"]
    Parser["parse_jsonstat2()"]
end

%% =========================
%% EXTERNAL
%% =========================
subgraph External["External"]
    SSB["SSB API"]
end

%% =========================
%% PIPELINE
%% =========================
subgraph Pipeline["Lakehouse Pipeline"]
    PipelineClass["PensjonLakehousePipeline"]

    BronzeStage["BronzeStage"]
    SilverStage["SilverStage"]
    GoldStage["GoldStage"]
end

%% =========================
%% SUPPORT
%% =========================
subgraph Support["Support"]
    SQLLoader["sql_loader.py"]
    AuditWriter["AuditWriter"]
    StructurePrinter["LakehouseStructurePrinter"]
end

%% =========================
%% SQL FILE GROUPS
%% =========================
subgraph SQLFiles["SQL files: pensjon/sql/"]

    subgraph BronzeSQL["bronze/"]
        BronzeCopySQL["copy SQL files"]
    end

    subgraph SilverSQL["silver/"]
        SilverBuildSQL["build SQL files"]
    end

    subgraph GoldSQL["gold/"]
        GoldBuildSQL["build SQL files"]
        GoldSelectSQL["select SQL files"]
    end
end

%% =========================
%% REPORTING
%% =========================
subgraph Reporting["Reporting"]
    Notebook["Jupyter Notebook"]
    Matplotlib["Matplotlib"]
end

%% =========================
%% APP WIRING
%% =========================
Main --> Dependencies
Main --> Config
Main --> PipelineClass

Dependencies --> BefolkningRepo
Dependencies --> LonnRepo

Dependencies --> BefolkningDS
Dependencies --> LonnDS

Config --> PipelineClass

%% =========================
%% DATA ACCESS DEPENDENCIES
%% =========================
BefolkningRepo --> BefolkningDS
LonnRepo --> LonnDS

BefolkningRepo --> Parser
LonnRepo --> Parser

BefolkningDS --> SSBBase
LonnDS --> SSBBase

SSBBase --> SSB

%% =========================
%% PIPELINE DEPENDENCY INJECTION
%% =========================
PipelineClass -->|"deps, config"| BronzeStage
PipelineClass -->|"db, config"| SilverStage
PipelineClass -->|"db, config"| GoldStage

BronzeStage --> BefolkningRepo
BronzeStage --> LonnRepo

BronzeStage --> AuditWriter
PipelineClass --> StructurePrinter

%% =========================
%% SQL LOADING
%% =========================
BronzeStage -->|"load_sql(bronze/...)"| SQLLoader
SilverStage -->|"load_sql(silver/...)"| SQLLoader
GoldStage -->|"load_sql(gold/...)"| SQLLoader

SQLLoader --> BronzeCopySQL
SQLLoader --> SilverBuildSQL
SQLLoader --> GoldBuildSQL
SQLLoader --> GoldSelectSQL

%% =========================
%% REPORTING
%% =========================
GoldStage --> Notebook
Notebook --> Matplotlib

%% =========================
%% STYLING
%% =========================
style EntryPoint stroke:#000000,fill:#E1BEE7
style CompositionRoot stroke:#000000,fill:#E1BEE7
style DataAccess stroke:#000000,fill:#DCEDC8
style External stroke:#000000,fill:#FFAB91
style Pipeline stroke:#000000,fill:#BBDEFB
style Support stroke:#000000,fill:#D7CCC8
style SQLFiles stroke:#000000,fill:#EFEBE9
style BronzeSQL stroke:#000000,fill:#D7CCC8
style SilverSQL stroke:#000000,fill:#CFD8DC
style GoldSQL stroke:#000000,fill:#FFF59D
style Reporting stroke:#000000,fill:#B2DFDB