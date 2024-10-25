Certainly! Below is a comprehensive **schema description** for your `metabolites.yml` file. This schema outlines each variable present in the YAML structure, explaining what it represents, its data type, and any additional pertinent information. This documentation will help ensure consistency, clarity, and ease of use as you develop and expand your metabolic pathway simulation.

---

## **Metabolites YAML Schema Description**

### **Top-Level Structure**

- **`metabolites`** *(object)*:
  - **Description:** The root key containing all metabolite entries.
  - **Structure:** Each key within `metabolites` represents a unique metabolite name (e.g., `Acetyl-CoA`, `Citrate`, etc.).
  - **Example:**
    ```yaml
    metabolites:
      Acetyl-CoA:
        # Metabolite details
      Citrate:
        # Metabolite details
    ```

### **Metabolite Entry Structure**

Each metabolite under the `metabolites` key follows a structured format with specific fields. Below is a detailed description of each field within a metabolite entry.

---

#### **1. `quantity`** *(number)*

- **Description:** Represents the initial or default quantity of the metabolite in the simulation.
- **Default Value:** `10`
- **Unit:** Typically in arbitrary units or as defined in your simulation parameters.
- **Example:**
  ```yaml
  quantity: 10
  ```

---

#### **2. `type`** *(string)*

- **Description:** Categorizes the metabolite based on its role or classification within metabolic pathways.
- **Possible Values:** 
  - `Core Krebs Cycle Intermediate`
  - `Electron Carrier`
  - `High-Energy Molecule`
  - `Byproduct`
  - `Input`
  - `Linking Metabolite`
  - `Coenzyme`
  - `Anaplerotic Metabolite`
  - `Ketone Body`
  - `Glyoxylate Cycle Metabolite`
  - `Pentose Phosphate Pathway Metabolite`
  - `Reducing Agent`
  - `Fatty Acid Oxidation Metabolite`
  - `Allosteric Effector`
  - `Energy Status Indicator`
  - `Redox State Indicator`
  - `Environmental Factor`
  - `Environmental Condition`
  - `Reactive Oxygen Species (ROS)`
  - `Energy Status Indicator`
- **Example:**
  ```yaml
  type: Core Krebs Cycle Intermediate
  ```

---

#### **3. `description`** *(string)*

- **Description:** Provides a brief overview of the metabolite's role and significance within the metabolic pathways.
- **Example:**
  ```yaml
  description: The starting molecule that combines with oxaloacetate to form citrate, initiating the cycle.
  ```

---

#### **4. `meta`** *(object)*

- **Description:** Contains detailed metadata about the metabolite, encompassing various attributes that influence its behavior and interactions within the cell.
- **Subfields:** Detailed below.

---

### **`meta` Subfields**

#### **a. `molecular_formula`** *(string)*

- **Description:** The chemical formula representing the number and type of atoms in the metabolite.
- **Example:**
  ```yaml
  molecular_formula: C23H38N7O17P3S
  ```

#### **b. `pathway`** *(string or list of strings)*

- **Description:** Lists the metabolic pathways in which the metabolite is involved.
- **Example:**
  ```yaml
  pathway: TCA Cycle, Fatty Acid Oxidation
  ```
  *Or as a list:*
  ```yaml
  pathway:
    - TCA Cycle
    - Fatty Acid Oxidation
  ```

#### **c. `role`** *(string)*

- **Description:** Specifies the particular function or role the metabolite plays within its associated pathways.
- **Example:**
  ```yaml
  role: Combines with oxaloacetate to form citrate
  ```

#### **d. `concentration`** *(object)*

- **Description:** Details the concentration attributes of the metabolite within the cell.
- **Subfields:**
  - **`default`** *(number)*: The initial concentration value.
  - **`unit`** *(string)*: The unit of concentration (e.g., mM).
  - **`range`** *(object)*: Specifies the minimum and maximum concentration values.
    - **`min`** *(number)*: Minimum concentration.
    - **`max`** *(number)*: Maximum concentration.
- **Example:**
  ```yaml
  concentration:
    default: 10
    unit: mM
    range:
      min: 0.1
      max: 100
  ```

#### **e. `localization`** *(object)*

- **Description:** Indicates the cellular compartments where the metabolite is primarily located.
- **Subfields:**
  - **`compartments`** *(list of strings)*: Names of cellular compartments (e.g., Mitochondria, Cytosol).
- **Example:**
  ```yaml
  localization:
    compartments:
      - Mitochondria
      - Cytosol
  ```

#### **f. `kinetics`** *(object)*

- **Description:** Contains kinetic parameters that describe the reaction rates involving the metabolite.
- **Subfields:**
  - **`Km`** *(number)*: Michaelis-Menten constant in mM.
  - **`Vmax`** *(number)*: Maximum reaction velocity in μmol/min.
- **Example:**
  ```yaml
  kinetics:
    Km: 0.5  # in mM
    Vmax: 100  # in μmol/min
  ```

#### **g. `transport`** *(object)*

- **Description:** Details the mechanisms and transporters involved in moving the metabolite between cellular compartments.
- **Subfields:**
  - **`mechanism`** *(string)*: Type of transport (e.g., Active Transport, Passive Diffusion).
  - **`transporters`** *(list of strings)*: Names of transport proteins or channels facilitating transport.
- **Example:**
  ```yaml
  transport:
    mechanism: Active Transport
    transporters:
      - Acetyl-CoA Transporter
  ```

#### **h. `reactions`** *(list of objects)*

- **Description:** Enumerates all biochemical reactions that consume or produce the metabolite.
- **Subfields for Each Reaction:**
  - **`name`** *(string)*: Name of the reaction.
  - **`enzyme`** *(string)*: Enzyme catalyzing the reaction.
  - **`role`** *(string)*: The metabolite's role in the reaction (e.g., Substrate, Product).
- **Example:**
  ```yaml
  reactions:
    - name: Citrate Synthase Reaction
      enzyme: Citrate Synthase
      role: Substrate
    - name: Isocitrate Dehydrogenase Reaction
      enzyme: Isocitrate Dehydrogenase
      role: Product
  ```

#### **i. `chemical_properties`** *(object)*

- **Description:** Provides chemical characteristics of the metabolite that influence its behavior.
- **Subfields:**
  - **`pKa`** *(number)*: The acid dissociation constant.
  - **`solubility`** *(string)*: Solubility level (e.g., High, Moderate, Low).
  - **`stability`** *(string)*: Stability status (e.g., Stable, Unstable).
  - **`molecular_weight`** *(number)*: Molecular weight in grams per mole (g/mol).
- **Example:**
  ```yaml
  chemical_properties:
    pKa: 5.0
    solubility: High
    stability: Stable
    molecular_weight: 809.57  # g/mol
  ```

#### **j. `regulation`** *(object)*

- **Description:** Details regulatory mechanisms affecting the metabolite and its interactions with enzymes.
- **Subfields:**
  - **`allosteric_effects`** *(list of objects)*:
    - **`target_enzyme`** *(string)*: Enzyme affected by the metabolite.
    - **`effect`** *(string)*: Nature of the effect (e.g., Inhibition, Activation).
  - **`feedback_loops`** *(list of objects)*:
    - **`type`** *(string)*: Type of feedback (e.g., Negative Feedback, Positive Feedback).
    - **`source`** *(string)*: Metabolite or process providing the feedback signal.
- **Example:**
  ```yaml
  regulation:
    allosteric_effects:
      - target_enzyme: Phosphofructokinase-1
        effect: Inhibition
    feedback_loops:
      - type: Negative Feedback
        source: Citrate
  ```

#### **k. `interactions`** *(object)*

- **Description:** Lists other molecules or proteins that interact with the metabolite.
- **Subfields:**
  - **`binding_partners`** *(list of objects)*:
    - **`Enzyme`** *(string)*: Name of the enzyme interacting with the metabolite.
    - **`type`** *(string)*: Nature of the interaction (e.g., Substrate, Activator).
- **Example:**
  ```yaml
  interactions:
    binding_partners:
      - Enzyme: Citrate Synthase
        type: Substrate
  ```

#### **l. `state_changes`** *(object)*

- **Description:** Captures different chemical states or forms the metabolite can adopt.
- **Subfields:**
  - **`redox_state`** *(string or null)*: Redox state (e.g., NADH/NAD⁺). Use `null` if not applicable.
  - **`phosphorylation`** *(string)*: Phosphorylation status (e.g., Phosphorylated, Unphosphorylated).
  - **`isomers`** *(string or null)*: Isomeric forms (e.g., D-form, L-form). Use `null` if not applicable.
- **Example:**
  ```yaml
  state_changes:
    redox_state: None
    phosphorylation: Unphosphorylated
    isomers: None
  ```

#### **m. `thermodynamics`** *(object)*

- **Description:** Provides thermodynamic data related to reactions involving the metabolite.
- **Subfields:**
  - **`delta_G`** *(number)*: Gibbs free energy change in kilojoules per mole (kJ/mol).
- **Example:**
  ```yaml
  thermodynamics:
    delta_G: -30.5  # kJ/mol
  ```

#### **n. `flux`** *(object)*

- **Description:** Represents the metabolic fluxes associated with the metabolite.
- **Subfields:**
  - **`production_rate`** *(number)*: Rate of production in micromoles per minute (μmol/min).
  - **`consumption_rate`** *(number)*: Rate of consumption in micromoles per minute (μmol/min).
- **Example:**
  ```yaml
  flux:
    production_rate: 5  # μmol/min
    consumption_rate: 5  # μmol/min
  ```

#### **o. `synthesis`** *(object)*

- **Description:** Details the synthesis pathway and enzymes responsible for producing the metabolite.
- **Subfields:**
  - **`pathway`** *(string)*: Name of the metabolic pathway involved in synthesis.
  - **`enzyme`** *(string)*: Enzyme catalyzing the synthesis reaction.
- **Example:**
  ```yaml
  synthesis:
    pathway: Pyruvate Dehydrogenase Complex
    enzyme: Pyruvate Dehydrogenase
  ```

#### **p. `degradation`** *(object)*

- **Description:** Details the degradation pathway and enzymes responsible for breaking down the metabolite.
- **Subfields:**
  - **`pathway`** *(string)*: Name of the metabolic pathway involved in degradation.
  - **`enzyme`** *(string)*: Enzyme catalyzing the degradation reaction.
- **Example:**
  ```yaml
  degradation:
    pathway: Fatty Acid Oxidation
    enzyme: Acetyl-CoA Oxidase
  ```

#### **q. `genetic_regulation`** *(object)*

- **Description:** Links the metabolite to genetic elements that regulate its synthesis or degradation.
- **Subfields:**
  - **`genes`** *(list of objects)*:
    - **`name`** *(string)*: Name or identifier of the gene.
- **Example:**
  ```yaml
  genetic_regulation:
    genes:
      - name: ACS (Acetyl-CoA Synthase)
      - name: PDH (Pyruvate Dehydrogenase)
  ```

#### **r. `physiological_conditions`** *(object)*

- **Description:** Specifies how physiological parameters affect the metabolite.
- **Subfields:**
  - **`pH_dependence`** *(boolean or string)*: Indicates if metabolite behavior is pH-dependent.
  - **`temperature_dependence`** *(boolean or string)*: Indicates if metabolite behavior is temperature-dependent.
  - **`oxygen_dependence`** *(string)*: Level of oxygen dependence (e.g., High, Moderate, Low).
- **Example:**
  ```yaml
  physiological_conditions:
    pH_dependence: Yes
    temperature_dependence: Yes
    oxygen_dependence: High
  ```

#### **s. `isomers`** *(object)*

- **Description:** Details different isomeric forms of the metabolite and their biological activity.
- **Subfields:**
  - **`D_form`** *(string)*: Activity status of the D-form (e.g., Active, Inactive).
  - **`L_form`** *(string)*: Activity status of the L-form.
- **Example:**
  ```yaml
  isomers:
    D_form: Active
    L_form: Inactive
  ```

#### **t. `stoichiometry`** *(object)*

- **Description:** Specifies the stoichiometric coefficients of the metabolite in various reactions.
- **Subfields:**
  - **`reactions`** *(list of objects)*:
    - **`name`** *(string)*: Name of the reaction.
    - **`coefficient`** *(number)*: Stoichiometric coefficient (e.g., 1, 2).
- **Example:**
  ```yaml
  stoichiometry:
    reactions:
      - name: Citrate Synthase Reaction
        coefficient: 1
      - name: Isocitrate Dehydrogenase Reaction
        coefficient: 1
  ```

#### **u. `mass_charge`** *(object)*

- **Description:** Provides mass and charge information of the metabolite at physiological conditions.
- **Subfields:**
  - **`molecular_weight`** *(number)*: Molecular weight in grams per mole (g/mol).
  - **`charge`** *(number or string)*: Net charge of the metabolite (e.g., -1, +2).
- **Example:**
  ```yaml
  mass_charge:
    molecular_weight: 809.57  # g/mol
    charge: -1
  ```

#### **v. `visualization`** *(object)*

- **Description:** Contains references to visual representations of the metabolite's structure.
- **Subfields:**
  - **`structure_2D`** *(string)*: File path or URL to a 2D structural image (e.g., PNG).
  - **`structure_3D`** *(string)*: File path or URL to a 3D structural file (e.g., PDB).
- **Example:**
  ```yaml
  visualization:
    structure_2D: "structures/acetyl_coa_2d.png"
    structure_3D: "structures/acetyl_coa_3d.pdb"
  ```

#### **w. `energy_metrics`** *(object)*

- **Description:** Quantifies the metabolite's contribution to the cell's energy state.
- **Subfields:**
  - **`ATP_yield`** *(number)*: Amount of ATP produced or consumed by the metabolite.
- **Example:**
  ```yaml
  energy_metrics:
    ATP_yield: 3
  ```

#### **x. `experimental_data`** *(object)*

- **Description:** Incorporates real-world experimental data to validate and calibrate the simulation.
- **Subfields:**
  - **`concentration`** *(number)*: Experimentally measured concentration in millimolar (mM).
  - **`reference`** *(string)*: Citation or reference to the experimental study.
- **Example:**
  ```yaml
  experimental_data:
    concentration: 5.0  # mM
    reference: "Smith et al., 2020"
  ```

---

### **Comprehensive Example**

Here’s how all these fields come together in a complete metabolite entry:

```yaml
metabolites:
  Acetyl-CoA:
    quantity: 10
    type: Core Krebs Cycle Intermediate
    description: The starting molecule that combines with oxaloacetate to form citrate, initiating the cycle.
    meta:
      molecular_formula: C23H38N7O17P3S
      pathway: TCA Cycle, Fatty Acid Oxidation
      role: Combines with oxaloacetate to form citrate
      concentration:
        default: 10
        unit: mM
        range:
          min: 0.1
          max: 100
      localization:
        compartments:
          - Mitochondria
      kinetics:
        Km: 0.5  # in mM
        Vmax: 100  # in μmol/min
      transport:
        mechanism: Active Transport
        transporters:
          - Acetyl-CoA Transporter
      reactions:
        - name: Citrate Synthase Reaction
          enzyme: Citrate Synthase
          role: Substrate
      chemical_properties:
        pKa: 5.0
        solubility: High
        stability: Stable
        molecular_weight: 809.57  # g/mol
      regulation:
        allosteric_effects:
          - target_enzyme: Phosphofructokinase-1
            effect: Inhibition
        feedback_loops:
          - type: Negative Feedback
            source: Citrate
      interactions:
        binding_partners:
          - Enzyme: Citrate Synthase
            type: Substrate
      state_changes:
        redox_state: None
        phosphorylation: Unphosphorylated
        isomers: None
      thermodynamics:
        delta_G: -30.5  # kJ/mol
      flux:
        production_rate: 5  # μmol/min
        consumption_rate: 5  # μmol/min
      synthesis:
        pathway: Pyruvate Dehydrogenase Complex
        enzyme: Pyruvate Dehydrogenase
      degradation:
        pathway: Fatty Acid Oxidation
        enzyme: Acetyl-CoA Oxidase
      genetic_regulation:
        genes:
          - name: ACS (Acetyl-CoA Synthase)
      physiological_conditions:
        pH_dependence: Yes
        temperature_dependence: Yes
        oxygen_dependence: High
      isomers:
        D_form: Active
        L_form: Inactive
      stoichiometry:
        reactions:
          - name: Citrate Synthase Reaction
            coefficient: 1
      mass_charge:
        molecular_weight: 809.57  # g/mol
        charge: -1
      visualization:
        structure_2D: "structures/acetyl_coa_2d.png"
        structure_3D: "structures/acetyl_coa_3d.pdb"
      energy_metrics:
        ATP_yield: 3
      experimental_data:
        concentration: 5.0  # mM
        reference: "Smith et al., 2020"
```

---

### **Detailed Field Descriptions**

Below is an expanded description of each field to provide clarity on their purpose and usage.

#### **Top-Level Key**

- **`metabolites`**:
  - **Type:** Object
  - **Description:** Encapsulates all metabolites involved in the simulation.
  - **Usage:** Each child key under `metabolites` represents a unique metabolite.

#### **Metabolite Fields**

1. **`quantity`**
   - **Type:** Number
   - **Description:** Initial or default quantity of the metabolite. This value can be used as a starting point in simulations and may change based on metabolic fluxes.

2. **`type`**
   - **Type:** String
   - **Description:** Categorizes the metabolite based on its function or classification within metabolic networks.

3. **`description`**
   - **Type:** String
   - **Description:** A concise explanation of the metabolite's role and importance in metabolic pathways.

4. **`meta`**
   - **Type:** Object
   - **Description:** Contains detailed metadata that provides in-depth information about the metabolite, influencing its behavior and interactions.

   - **Subfields within `meta`:**

     - **`molecular_formula`**
       - **Type:** String
       - **Description:** Chemical formula indicating the number and types of atoms in the metabolite.

     - **`pathway`**
       - **Type:** String or List of Strings
       - **Description:** Metabolic pathways that incorporate the metabolite. Supports single or multiple pathways.

     - **`role`**
       - **Type:** String
       - **Description:** Specific function of the metabolite within its pathways.

     - **`concentration`**
       - **Type:** Object
       - **Description:** Details about the metabolite's concentration levels.

       - **Subfields:**
         - **`default`** *(Number)*: Baseline concentration value.
         - **`unit`** *(String)*: Measurement unit (e.g., mM).
         - **`range`** *(Object)*:
           - **`min`** *(Number)*: Minimum concentration observed or allowed.
           - **`max`** *(Number)*: Maximum concentration observed or allowed.

     - **`localization`**
       - **Type:** Object
       - **Description:** Cellular compartments where the metabolite is primarily located.

       - **Subfields:**
         - **`compartments`** *(List of Strings)*: Names of compartments (e.g., Mitochondria).

     - **`kinetics`**
       - **Type:** Object
       - **Description:** Kinetic parameters governing the metabolite's interactions in reactions.

       - **Subfields:**
         - **`Km`** *(Number)*: Michaelis-Menten constant, indicating the affinity of the enzyme for the metabolite.
         - **`Vmax`** *(Number)*: Maximum rate of the reaction involving the metabolite.

     - **`transport`**
       - **Type:** Object
       - **Description:** Information about the transport mechanisms and proteins facilitating metabolite movement.

       - **Subfields:**
         - **`mechanism`** *(String)*: Type of transport (e.g., Active Transport).
         - **`transporters`** *(List of Strings)*: Names of transport proteins involved.

     - **`reactions`**
       - **Type:** List of Objects
       - **Description:** Reactions that consume or produce the metabolite.

       - **Each Reaction Object Contains:**
         - **`name`** *(String)*: Name of the reaction.
         - **`enzyme`** *(String)*: Enzyme catalyzing the reaction.
         - **`role`** *(String)*: Metabolite's role (e.g., Substrate, Product).

     - **`chemical_properties`**
       - **Type:** Object
       - **Description:** Chemical characteristics influencing metabolite behavior.

       - **Subfields:**
         - **`pKa`** *(Number)*: Acid dissociation constant.
         - **`solubility`** *(String)*: Solubility level.
         - **`stability`** *(String)*: Stability status.
         - **`molecular_weight`** *(Number)*: Molecular weight in g/mol.

     - **`regulation`**
       - **Type:** Object
       - **Description:** Regulatory mechanisms affecting metabolite and enzyme activities.

       - **Subfields:**
         - **`allosteric_effects`** *(List of Objects)*:
           - **`target_enzyme`** *(String)*: Enzyme affected.
           - **`effect`** *(String)*: Nature of effect (e.g., Inhibition).
         - **`feedback_loops`** *(List of Objects)*:
           - **`type`** *(String)*: Feedback type (e.g., Negative Feedback).
           - **`source`** *(String)*: Source metabolite or process providing feedback.

     - **`interactions`**
       - **Type:** Object
       - **Description:** Interactions with other molecules or proteins.

       - **Subfields:**
         - **`binding_partners`** *(List of Objects)*:
           - **`Enzyme`** *(String)*: Enzyme interacting with the metabolite.
           - **`type`** *(String)*: Nature of interaction (e.g., Substrate).

     - **`state_changes`**
       - **Type:** Object
       - **Description:** Different chemical states or forms the metabolite can adopt.

       - **Subfields:**
         - **`redox_state`** *(String or null)*: Redox state (e.g., NADH/NAD⁺). Use `null` if not applicable.
         - **`phosphorylation`** *(String)*: Phosphorylation status (e.g., Phosphorylated).
         - **`isomers`** *(String or null)*: Isomeric forms (e.g., D-form). Use `null` if not applicable.

     - **`thermodynamics`**
       - **Type:** Object
       - **Description:** Thermodynamic parameters related to reactions involving the metabolite.

       - **Subfields:**
         - **`delta_G`** *(Number)*: Gibbs free energy change in kJ/mol.

     - **`flux`**
       - **Type:** Object
       - **Description:** Metabolic fluxes indicating production and consumption rates.

       - **Subfields:**
         - **`production_rate`** *(Number)*: Rate of production in μmol/min.
         - **`consumption_rate`** *(Number)*: Rate of consumption in μmol/min.

     - **`synthesis`**
       - **Type:** Object
       - **Description:** Information about the synthesis of the metabolite.

       - **Subfields:**
         - **`pathway`** *(String)*: Metabolic pathway responsible for synthesis.
         - **`enzyme`** *(String)*: Enzyme catalyzing synthesis.

     - **`degradation`**
       - **Type:** Object
       - **Description:** Information about the degradation of the metabolite.

       - **Subfields:**
         - **`pathway`** *(String)*: Metabolic pathway responsible for degradation.
         - **`enzyme`** *(String)*: Enzyme catalyzing degradation.

     - **`genetic_regulation`**
       - **Type:** Object
       - **Description:** Links between the metabolite and genetic elements regulating its metabolism.

       - **Subfields:**
         - **`genes`** *(List of Objects)*:
           - **`name`** *(String)*: Gene name or identifier.

     - **`physiological_conditions`**
       - **Type:** Object
       - **Description:** How physiological parameters affect the metabolite's behavior.

       - **Subfields:**
         - **`pH_dependence`** *(Boolean or String)*: Indicates pH dependence (`Yes`, `No`).
         - **`temperature_dependence`** *(Boolean or String)*: Indicates temperature dependence (`Yes`, `No`).
         - **`oxygen_dependence`** *(String)*: Level of oxygen dependence (`High`, `Moderate`, `Low`).

     - **`isomers`**
       - **Type:** Object
       - **Description:** Details about different isomeric forms of the metabolite and their activities.

       - **Subfields:**
         - **`D_form`** *(String)*: Activity status of the D-form (`Active`, `Inactive`).
         - **`L_form`** *(String)*: Activity status of the L-form (`Active`, `Inactive`).

     - **`stoichiometry`**
       - **Type:** Object
       - **Description:** Stoichiometric coefficients of the metabolite in various reactions.

       - **Subfields:**
         - **`reactions`** *(List of Objects)*:
           - **`name`** *(String)*: Reaction name.
           - **`coefficient`** *(Number)*: Stoichiometric coefficient.

     - **`mass_charge`**
       - **Type:** Object
       - **Description:** Mass and charge information of the metabolite at physiological pH.

       - **Subfields:**
         - **`molecular_weight`** *(Number)*: Molecular weight in g/mol.
         - **`charge`** *(Number or String)*: Net charge (e.g., `-1`).

     - **`visualization`**
       - **Type:** Object
       - **Description:** References to visual representations of the metabolite's structure.

       - **Subfields:**
         - **`structure_2D`** *(String)*: File path or URL to a 2D structural image.
         - **`structure_3D`** *(String)*: File path or URL to a 3D structural file.

     - **`energy_metrics`**
       - **Type:** Object
       - **Description:** Quantifies the metabolite's contribution to the cell's energy state.

       - **Subfields:**
         - **`ATP_yield`** *(Number)*: Amount of ATP produced or consumed.

     - **`experimental_data`**
       - **Type:** Object
       - **Description:** Incorporates real-world data to validate simulation parameters.

       - **Subfields:**
         - **`concentration`** *(Number)*: Experimentally measured concentration in mM.
         - **`reference`** *(String)*: Citation for the experimental data.

---

### **Data Types Overview**

- **`number`**: Numeric values, can be integers or decimals.
- **`string`**: Textual data.
- **`boolean`**: `Yes` or `No` (can be represented as `true` or `false` in some contexts).
- **`list`**: Ordered collection of items (e.g., list of strings or objects).
- **`object`**: Nested key-value pairs encapsulating related data.

---

### **Guidelines for Using the Schema**

1. **Consistency in Naming:**
   - Use standardized and descriptive names for metabolites to avoid confusion.
   - Ensure that naming conventions are consistent across all entries.

2. **Units Specification:**
   - Always specify units for quantitative fields to maintain clarity and avoid ambiguity.
   - Common units include mM (millimolar), μmol/min (micromoles per minute), g/mol (grams per mole), etc.

3. **Completeness of Data:**
   - Populate all relevant fields to enhance the simulation's accuracy.
   - If certain fields are not applicable to a metabolite, they can be set to `null` or omitted, depending on your simulation requirements.

4. **Modularity and Scalability:**
   - Structure the YAML file to allow easy addition of new metabolites or attributes.
   - Consider using anchors and aliases in YAML for repetitive structures to reduce redundancy.

5. **Validation and Error Checking:**
   - Use YAML validators to ensure the file is correctly formatted.
   - Cross-reference with biological databases (e.g., KEGG, MetaCyc, ChEBI) to verify the accuracy of data.

6. **Documentation and References:**
   - Include references for experimental data to provide sources for validation.
   - Document any assumptions or simplifications made in the simulation parameters.

7. **Flexibility for Simulation Needs:**
   - Adapt the schema to include additional fields as your simulation evolves.
   - For specialized simulations, you might need to incorporate unique attributes not covered in this schema.

---

### **Extended Schema Example for Multiple Metabolites**

Below is an example showcasing how multiple metabolites can be structured within the YAML file using the described schema.

```yaml
metabolites:
  Acetyl-CoA:
    quantity: 10
    type: Core Krebs Cycle Intermediate
    description: The starting molecule that combines with oxaloacetate to form citrate, initiating the cycle.
    meta:
      molecular_formula: C23H38N7O17P3S
      pathway:
        - TCA Cycle
        - Fatty Acid Oxidation
      role: Combines with oxaloacetate to form citrate
      concentration:
        default: 10
        unit: mM
        range:
          min: 0.1
          max: 100
      localization:
        compartments:
          - Mitochondria
      kinetics:
        Km: 0.5  # in mM
        Vmax: 100  # in μmol/min
      transport:
        mechanism: Active Transport
        transporters:
          - Acetyl-CoA Transporter
      reactions:
        - name: Citrate Synthase Reaction
          enzyme: Citrate Synthase
          role: Substrate
      chemical_properties:
        pKa: 5.0
        solubility: High
        stability: Stable
        molecular_weight: 809.57  # g/mol
      regulation:
        allosteric_effects:
          - target_enzyme: Phosphofructokinase-1
            effect: Inhibition
        feedback_loops:
          - type: Negative Feedback
            source: Citrate
      interactions:
        binding_partners:
          - Enzyme: Citrate Synthase
            type: Substrate
      state_changes:
        redox_state: None
        phosphorylation: Unphosphorylated
        isomers: None
      thermodynamics:
        delta_G: -30.5  # kJ/mol
      flux:
        production_rate: 5  # μmol/min
        consumption_rate: 5  # μmol/min
      synthesis:
        pathway: Pyruvate Dehydrogenase Complex
        enzyme: Pyruvate Dehydrogenase
      degradation:
        pathway: Fatty Acid Oxidation
        enzyme: Acetyl-CoA Oxidase
      genetic_regulation:
        genes:
          - name: ACS (Acetyl-CoA Synthase)
      physiological_conditions:
        pH_dependence: Yes
        temperature_dependence: Yes
        oxygen_dependence: High
      isomers:
        D_form: Active
        L_form: Inactive
      stoichiometry:
        reactions:
          - name: Citrate Synthase Reaction
            coefficient: 1
      mass_charge:
        molecular_weight: 809.57  # g/mol
        charge: -1
      visualization:
        structure_2D: "structures/acetyl_coa_2d.png"
        structure_3D: "structures/acetyl_coa_3d.pdb"
      energy_metrics:
        ATP_yield: 3
      experimental_data:
        concentration: 5.0  # mM
        reference: "Smith et al., 2020"

  Citrate:
    quantity: 10
    type: Core Krebs Cycle Intermediate
    description: Formed from acetyl-CoA and oxaloacetate; the first product of the cycle.
    meta:
      molecular_formula: C6H8O7
      pathway:
        - TCA Cycle
      role: Precursor for isocitrate formation
      concentration:
        default: 10
        unit: mM
        range:
          min: 0.5
          max: 30
      localization:
        compartments:
          - Mitochondria
      kinetics:
        Km: 0.2  # in mM
        Vmax: 50  # in μmol/min
      transport:
        mechanism: Passive Diffusion
        transporters:
          - Citrate Transporter
      reactions:
        - name: Citrate Synthase Reaction
          enzyme: Citrate Synthase
          role: Product
        - name: ATP Citrate Lyase Reaction
          enzyme: ATP Citrate Lyase
          role: Substrate
      chemical_properties:
        pKa: 3.1
        solubility: Moderate
        stability: Stable
        molecular_weight: 192.13  # g/mol
      regulation:
        allosteric_effects:
          - target_enzyme: Isocitrate Dehydrogenase
            effect: Activation
        feedback_loops:
          - type: Positive Feedback
            source: Acetyl-CoA
      interactions:
        binding_partners:
          - Enzyme: Isocitrate Dehydrogenase
            type: Activator
      state_changes:
        redox_state: None
        phosphorylation: Unphosphorylated
        isomers: None
      thermodynamics:
        delta_G: -10.5  # kJ/mol
      flux:
        production_rate: 5  # μmol/min
        consumption_rate: 5  # μmol/min
      synthesis:
        pathway: TCA Cycle
        enzyme: Citrate Synthase
      degradation:
        pathway: Glycolysis Regulation
        enzyme: ATP Citrate Lyase
      genetic_regulation:
        genes:
          - name: CS (Citrate Synthase)
      physiological_conditions:
        pH_dependence: Yes
        temperature_dependence: Yes
        oxygen_dependence: Moderate
      isomers:
        D_form: Active
        L_form: Inactive
      stoichiometry:
        reactions:
          - name: Citrate Synthase Reaction
            coefficient: 1
          - name: ATP Citrate Lyase Reaction
            coefficient: 1
      mass_charge:
        molecular_weight: 192.13  # g/mol
        charge: -3
      visualization:
        structure_2D: "structures/citrate_2d.png"
        structure_3D: "structures/citrate_3d.pdb"
      energy_metrics:
        ATP_yield: 2
      experimental_data:
        concentration: 8.0  # mM
        reference: "Doe et al., 2019"
```

---

### **Additional Considerations**

1. **Optional Fields:**
   - Not all fields may be applicable to every metabolite. For such cases, you can:
     - Omit the field entirely.
     - Set the field to `null` or `N/A`.

2. **Units Consistency:**
   - Ensure that units are consistent across all metabolite entries to maintain simulation accuracy.
   - Common units used:
     - **Concentration:** mM (millimolar)
     - **Reaction Rates:** μmol/min (micromoles per minute)
     - **Molecular Weight:** g/mol (grams per mole)
     - **Gibbs Free Energy:** kJ/mol (kilojoules per mole)

3. **Naming Conventions:**
   - Use standardized naming for metabolites to facilitate cross-referencing with biological databases.
   - Consider adopting identifiers from databases like KEGG, MetaCyc, or ChEBI for interoperability.

4. **Validation:**
   - Regularly validate your YAML structure using YAML linters or validators to prevent syntax errors.
   - Cross-reference metabolite data with reliable biological databases to ensure accuracy.

5. **Extensibility:**
   - Design the schema to accommodate future expansions, such as adding new metabolites or integrating additional attributes like genetic interactions or disease associations.

6. **Documentation:**
   - Maintain thorough documentation for your YAML schema, especially if collaborating with others, to ensure clarity and ease of use.

---

### **Summary of Fields and Their Representations**

| **Field Path**                | **Data Type**      | **Description**                                                                                       |
|-------------------------------|--------------------|-------------------------------------------------------------------------------------------------------|
| `metabolites`                 | Object             | Root container for all metabolite entries.                                                            |
| `metabolites.<MetaboliteName>`| Object             | Individual metabolite entry containing detailed attributes.                                           |
| `quantity`                    | Number             | Initial or default quantity of the metabolite.                                                        |
| `type`                        | String             | Category or classification of the metabolite.                                                         |
| `description`                 | String             | Brief overview of the metabolite's role.                                                              |
| `meta`                        | Object             | Nested container for detailed metadata about the metabolite.                                         |
| `meta.molecular_formula`      | String             | Chemical formula of the metabolite.                                                                   |
| `meta.pathway`                | String/List        | Metabolic pathways involving the metabolite.                                                          |
| `meta.role`                   | String             | Specific function of the metabolite within its pathways.                                             |
| `meta.concentration`          | Object             | Concentration details, including default value, unit, and range.                                     |
| `meta.concentration.default`  | Number             | Default concentration value.                                                                          |
| `meta.concentration.unit`     | String             | Unit of concentration (e.g., mM).                                                                     |
| `meta.concentration.range`    | Object             | Defines the minimum and maximum concentration values.                                                 |
| `meta.concentration.range.min`| Number             | Minimum concentration.                                                                                 |
| `meta.concentration.range.max`| Number             | Maximum concentration.                                                                                 |
| `meta.localization`           | Object             | Cellular compartments where the metabolite is located.                                                |
| `meta.localization.compartments`| List of Strings | Names of compartments (e.g., Mitochondria).                                                           |
| `meta.kinetics`               | Object             | Kinetic parameters governing metabolite's reactions.                                                 |
| `meta.kinetics.Km`            | Number             | Michaelis-Menten constant.                                                                            |
| `meta.kinetics.Vmax`          | Number             | Maximum reaction velocity.                                                                             |
| `meta.transport`              | Object             | Transport mechanisms and associated transporters.                                                     |
| `meta.transport.mechanism`    | String             | Type of transport (e.g., Active Transport).                                                           |
| `meta.transport.transporters` | List of Strings    | Names of transport proteins involved.                                                                  |
| `meta.reactions`              | List of Objects    | Biochemical reactions involving the metabolite.                                                       |
| `meta.reactions.name`         | String             | Name of the reaction.                                                                                   |
| `meta.reactions.enzyme`       | String             | Enzyme catalyzing the reaction.                                                                        |
| `meta.reactions.role`         | String             | Metabolite's role in the reaction (e.g., Substrate, Product).                                         |
| `meta.chemical_properties`    | Object             | Chemical characteristics of the metabolite.                                                           |
| `meta.chemical_properties.pKa`| Number             | Acid dissociation constant.                                                                            |
| `meta.chemical_properties.solubility`| String    | Solubility level.                                                                                       |
| `meta.chemical_properties.stability`| String     | Stability status.                                                                                       |
| `meta.chemical_properties.molecular_weight`| Number | Molecular weight in g/mol.                                                                             |
| `meta.regulation`             | Object             | Regulatory mechanisms affecting the metabolite.                                                       |
| `meta.regulation.allosteric_effects`| List of Objects| Allosteric effects on target enzymes.                                                                  |
| `meta.regulation.allosteric_effects.target_enzyme`| String | Enzyme affected by allosteric regulation.                                                              |
| `meta.regulation.allosteric_effects.effect`| String | Nature of the effect (e.g., Inhibition).                                                               |
| `meta.regulation.feedback_loops`| List of Objects   | Feedback loops involving the metabolite.                                                               |
| `meta.regulation.feedback_loops.type`| String     | Type of feedback (e.g., Negative Feedback).                                                            |
| `meta.regulation.feedback_loops.source`| String   | Source providing the feedback signal.                                                                   |
| `meta.interactions`           | Object             | Interactions with other molecules or proteins.                                                         |
| `meta.interactions.binding_partners`| List of Objects | Binding partners interacting with the metabolite.                                                        |
| `meta.interactions.binding_partners.Enzyme`| String | Name of the binding enzyme.                                                                             |
| `meta.interactions.binding_partners.type`| String   | Type of interaction (e.g., Substrate).                                                                 |
| `meta.state_changes`          | Object             | Different chemical states or forms the metabolite can adopt.                                          |
| `meta.state_changes.redox_state`| String or null   | Redox state (if applicable).                                                                            |
| `meta.state_changes.phosphorylation`| String       | Phosphorylation status.                                                                                  |
| `meta.state_changes.isomers`  | String or null     | Isomeric forms (if applicable).                                                                         |
| `meta.thermodynamics`         | Object             | Thermodynamic parameters related to the metabolite's reactions.                                       |
| `meta.thermodynamics.delta_G` | Number             | Gibbs free energy change in kJ/mol.                                                                    |
| `meta.flux`                   | Object             | Metabolic fluxes indicating production and consumption rates.                                         |
| `meta.flux.production_rate`   | Number             | Rate of production in μmol/min.                                                                         |
| `meta.flux.consumption_rate`  | Number             | Rate of consumption in μmol/min.                                                                        |
| `meta.synthesis`              | Object             | Information about the metabolite's synthesis.                                                           |
| `meta.synthesis.pathway`      | String             | Metabolic pathway responsible for synthesis.                                                            |
| `meta.synthesis.enzyme`       | String             | Enzyme catalyzing synthesis.                                                                             |
| `meta.degradation`            | Object             | Information about the metabolite's degradation.                                                         |
| `meta.degradation.pathway`    | String             | Metabolic pathway responsible for degradation.                                                          |
| `meta.degradation.enzyme`     | String             | Enzyme catalyzing degradation.                                                                           |
| `meta.genetic_regulation`     | Object             | Genetic elements regulating the metabolite's metabolism.                                               |
| `meta.genetic_regulation.genes`| List of Objects   | Genes involved in regulating the metabolite.                                                             |
| `meta.genetic_regulation.genes.name`| String     | Gene name or identifier.                                                                                  |
| `meta.physiological_conditions`| Object            | How physiological parameters affect the metabolite.                                                     |
| `meta.physiological_conditions.pH_dependence`| Boolean/String | Indicates pH dependence.                                                                                  |
| `meta.physiological_conditions.temperature_dependence`| Boolean/String | Indicates temperature dependence.                                                                        |
| `meta.physiological_conditions.oxygen_dependence`| String | Level of oxygen dependence (e.g., High).                                                                  |
| `meta.isomers`                | Object             | Details about different isomeric forms and their activities.                                           |
| `meta.isomers.D_form`          | String             | Activity status of the D-form (e.g., Active).                                                           |
| `meta.isomers.L_form`          | String             | Activity status of the L-form (e.g., Inactive).                                                         |
| `meta.stoichiometry`          | Object             | Stoichiometric coefficients of the metabolite in various reactions.                                    |
| `meta.stoichiometry.reactions`| List of Objects    | Reactions involving the metabolite and their coefficients.                                             |
| `meta.stoichiometry.reactions.name`| String       | Name of the reaction.                                                                                     |
| `meta.stoichiometry.reactions.coefficient`| Number | Stoichiometric coefficient in the reaction.                                                               |
| `meta.mass_charge`            | Object             | Mass and charge information of the metabolite.                                                          |
| `meta.mass_charge.molecular_weight`| Number        | Molecular weight in g/mol.                                                                                |
| `meta.mass_charge.charge`     | Number/String      | Net charge of the metabolite (e.g., `-1`).                                                               |
| `meta.visualization`          | Object             | References to visual representations of the metabolite's structure.                                     |
| `meta.visualization.structure_2D`| String          | File path or URL to a 2D structural image (e.g., PNG).                                                 |
| `meta.visualization.structure_3D`| String          | File path or URL to a 3D structural file (e.g., PDB).                                                  |
| `meta.energy_metrics`         | Object             | Quantifies the metabolite's contribution to the cell's energy state.                                     |
| `meta.energy_metrics.ATP_yield`| Number           | Amount of ATP produced or consumed by the metabolite.                                                   |
| `meta.experimental_data`      | Object             | Real-world experimental data for validation and calibration.                                           |
| `meta.experimental_data.concentration`| Number    | Experimentally measured concentration in mM.                                                             |
| `meta.experimental_data.reference`| String         | Citation or reference to the experimental study providing the data.                                    |

---

### **Example Schema Description**

To illustrate how each field is represented and described, here's a detailed breakdown of the `Acetyl-CoA` metabolite entry:

```yaml
metabolites:
  Acetyl-CoA:
    quantity: 10
    type: Core Krebs Cycle Intermediate
    description: The starting molecule that combines with oxaloacetate to form citrate, initiating the cycle.
    meta:
      molecular_formula: C23H38N7O17P3S
      pathway: TCA Cycle, Fatty Acid Oxidation
      role: Combines with oxaloacetate to form citrate
      concentration:
        default: 10
        unit: mM
        range:
          min: 0.1
          max: 100
      localization:
        compartments:
          - Mitochondria
      kinetics:
        Km: 0.5  # in mM
        Vmax: 100  # in μmol/min
      transport:
        mechanism: Active Transport
        transporters:
          - Acetyl-CoA Transporter
      reactions:
        - name: Citrate Synthase Reaction
          enzyme: Citrate Synthase
          role: Substrate
      chemical_properties:
        pKa: 5.0
        solubility: High
        stability: Stable
        molecular_weight: 809.57  # g/mol
      regulation:
        allosteric_effects:
          - target_enzyme: Phosphofructokinase-1
            effect: Inhibition
        feedback_loops:
          - type: Negative Feedback
            source: Citrate
      interactions:
        binding_partners:
          - Enzyme: Citrate Synthase
            type: Substrate
      state_changes:
        redox_state: None
        phosphorylation: Unphosphorylated
        isomers: None
      thermodynamics:
        delta_G: -30.5  # kJ/mol
      flux:
        production_rate: 5  # μmol/min
        consumption_rate: 5  # μmol/min
      synthesis:
        pathway: Pyruvate Dehydrogenase Complex
        enzyme: Pyruvate Dehydrogenase
      degradation:
        pathway: Fatty Acid Oxidation
        enzyme: Acetyl-CoA Oxidase
      genetic_regulation:
        genes:
          - name: ACS (Acetyl-CoA Synthase)
      physiological_conditions:
        pH_dependence: Yes
        temperature_dependence: Yes
        oxygen_dependence: High
      isomers:
        D_form: Active
        L_form: Inactive
      stoichiometry:
        reactions:
          - name: Citrate Synthase Reaction
            coefficient: 1
      mass_charge:
        molecular_weight: 809.57  # g/mol
        charge: -1
      visualization:
        structure_2D: "structures/acetyl_coa_2d.png"
        structure_3D: "structures/acetyl_coa_3d.pdb"
      energy_metrics:
        ATP_yield: 3
      experimental_data:
        concentration: 5.0  # mM
        reference: "Smith et al., 2020"
```

**Field Breakdown:**

- **`quantity: 10`**
  - **Type:** Number
  - **Represents:** Initial quantity of Acetyl-CoA in the simulation.

- **`type: Core Krebs Cycle Intermediate`**
  - **Type:** String
  - **Represents:** Classification of Acetyl-CoA as a central component of the Krebs Cycle.

- **`description: The starting molecule that combines with oxaloacetate to form citrate, initiating the cycle.`**
  - **Type:** String
  - **Represents:** Brief role of Acetyl-CoA in the Krebs Cycle.

- **`meta:`**
  - **Type:** Object
  - **Contains:** Detailed metadata about Acetyl-CoA.

  - **`molecular_formula: C23H38N7O17P3S`**
    - **Type:** String
    - **Represents:** Chemical formula of Acetyl-CoA.

  - **`pathway: TCA Cycle, Fatty Acid Oxidation`**
    - **Type:** String/List
    - **Represents:** Metabolic pathways involving Acetyl-CoA.

  - **`role: Combines with oxaloacetate to form citrate`**
    - **Type:** String
    - **Represents:** Specific function in the TCA Cycle.

  - **`concentration:`**
    - **Type:** Object
    - **Represents:** Concentration details of Acetyl-CoA.

    - **`default: 10`**
      - **Type:** Number
      - **Represents:** Default concentration value.

    - **`unit: mM`**
      - **Type:** String
      - **Represents:** Unit of concentration.

    - **`range:`**
      - **Type:** Object
      - **Represents:** Acceptable concentration range.

      - **`min: 0.1`**
        - **Type:** Number
        - **Represents:** Minimum concentration.

      - **`max: 100`**
        - **Type:** Number
        - **Represents:** Maximum concentration.

  - **`localization:`**
    - **Type:** Object
    - **Represents:** Cellular compartments containing Acetyl-CoA.

    - **`compartments:`**
      - **Type:** List of Strings
      - **Represents:** Names of compartments (e.g., Mitochondria).

  - **`kinetics:`**
    - **Type:** Object
    - **Represents:** Kinetic parameters for reactions involving Acetyl-CoA.

    - **`Km: 0.5`**
      - **Type:** Number
      - **Represents:** Michaelis-Menten constant in mM.

    - **`Vmax: 100`**
      - **Type:** Number
      - **Represents:** Maximum reaction velocity in μmol/min.

  - **`transport:`**
    - **Type:** Object
    - **Represents:** Transport mechanisms and transporters for Acetyl-CoA.

    - **`mechanism: Active Transport`**
      - **Type:** String
      - **Represents:** Type of transport mechanism.

    - **`transporters:`**
      - **Type:** List of Strings
      - **Represents:** Names of transport proteins.

  - **`reactions:`**
    - **Type:** List of Objects
    - **Represents:** Reactions involving Acetyl-CoA.

    - **First Reaction Object:**
      - **`name: Citrate Synthase Reaction`**
        - **Type:** String
        - **Represents:** Name of the reaction.
      - **`enzyme: Citrate Synthase`**
        - **Type:** String
        - **Represents:** Enzyme catalyzing the reaction.
      - **`role: Substrate`**
        - **Type:** String
        - **Represents:** Acetyl-CoA's role in the reaction.

  - **`chemical_properties:`**
    - **Type:** Object
    - **Represents:** Chemical characteristics of Acetyl-CoA.

    - **`pKa: 5.0`**
      - **Type:** Number
      - **Represents:** Acid dissociation constant.

    - **`solubility: High`**
      - **Type:** String
      - **Represents:** Solubility level.

    - **`stability: Stable`**
      - **Type:** String
      - **Represents:** Stability status.

    - **`molecular_weight: 809.57`**
      - **Type:** Number
      - **Represents:** Molecular weight in g/mol.

  - **`regulation:`**
    - **Type:** Object
    - **Represents:** Regulatory mechanisms affecting Acetyl-CoA.

    - **`allosteric_effects:`**
      - **Type:** List of Objects
      - **Represents:** Allosteric regulation details.

      - **First Allosteric Effect Object:**
        - **`target_enzyme: Phosphofructokinase-1`**
          - **Type:** String
          - **Represents:** Enzyme affected.
        - **`effect: Inhibition`**
          - **Type:** String
          - **Represents:** Nature of effect.

    - **`feedback_loops:`**
      - **Type:** List of Objects
      - **Represents:** Feedback mechanisms.

      - **First Feedback Loop Object:**
        - **`type: Negative Feedback`**
          - **Type:** String
          - **Represents:** Type of feedback.
        - **`source: Citrate`**
          - **Type:** String
          - **Represents:** Source providing feedback.

  - **`interactions:`**
    - **Type:** Object
    - **Represents:** Interactions with other molecules or enzymes.

    - **`binding_partners:`**
      - **Type:** List of Objects
      - **Represents:** Binding partners.

      - **First Binding Partner Object:**
        - **`Enzyme: Citrate Synthase`**
          - **Type:** String
          - **Represents:** Enzyme interacting with Acetyl-CoA.
        - **`type: Substrate`**
          - **Type:** String
          - **Represents:** Nature of interaction.

  - **`state_changes:`**
    - **Type:** Object
    - **Represents:** Chemical state variations of Acetyl-CoA.

    - **`redox_state: None`**
      - **Type:** String or Null
      - **Represents:** Redox state (not applicable here).

    - **`phosphorylation: Unphosphorylated`**
      - **Type:** String
      - **Represents:** Phosphorylation status.

    - **`isomers: None`**
      - **Type:** String or Null
      - **Represents:** Isomeric forms (not applicable here).

  - **`thermodynamics:`**
    - **Type:** Object
    - **Represents:** Thermodynamic data related to Acetyl-CoA.

    - **`delta_G: -30.5`**
      - **Type:** Number
      - **Represents:** Gibbs free energy change in kJ/mol.

  - **`flux:`**
    - **Type:** Object
    - **Represents:** Metabolic flux rates.

    - **`production_rate: 5`**
      - **Type:** Number
      - **Represents:** Production rate in μmol/min.

    - **`consumption_rate: 5`**
      - **Type:** Number
      - **Represents:** Consumption rate in μmol/min.

  - **`synthesis:`**
    - **Type:** Object
    - **Represents:** Synthesis details of Acetyl-CoA.

    - **`pathway: Pyruvate Dehydrogenase Complex`**
      - **Type:** String
      - **Represents:** Pathway involved in synthesis.

    - **`enzyme: Pyruvate Dehydrogenase`**
      - **Type:** String
      - **Represents:** Enzyme catalyzing synthesis.

  - **`degradation:`**
    - **Type:** Object
    - **Represents:** Degradation details of Acetyl-CoA.

    - **`pathway: Fatty Acid Oxidation`**
      - **Type:** String
      - **Represents:** Pathway involved in degradation.

    - **`enzyme: Acetyl-CoA Oxidase`**
      - **Type:** String
      - **Represents:** Enzyme catalyzing degradation.

  - **`genetic_regulation:`**
    - **Type:** Object
    - **Represents:** Genes regulating Acetyl-CoA metabolism.

    - **`genes:`**
      - **Type:** List of Objects
      - **Represents:** Genes involved.

      - **First Gene Object:**
        - **`name: ACS (Acetyl-CoA Synthase)`**
          - **Type:** String
          - **Represents:** Gene name.

  - **`physiological_conditions:`**
    - **Type:** Object
    - **Represents:** Environmental and physiological factors affecting Acetyl-CoA.

    - **`pH_dependence: Yes`**
      - **Type:** Boolean/String
      - **Represents:** Indicates pH dependence.

    - **`temperature_dependence: Yes`**
      - **Type:** Boolean/String
      - **Represents:** Indicates temperature dependence.

    - **`oxygen_dependence: High`**
      - **Type:** String
      - **Represents:** Level of oxygen dependence.

  - **`isomers:`**
    - **Type:** Object
    - **Represents:** Isomeric forms of Acetyl-CoA.

    - **`D_form: Active`**
      - **Type:** String
      - **Represents:** Activity status of the D-form.

    - **`L_form: Inactive`**
      - **Type:** String
      - **Represents:** Activity status of the L-form.

  - **`stoichiometry:`**
    - **Type:** Object
    - **Represents:** Stoichiometric coefficients in reactions.

    - **`reactions:`**
      - **Type:** List of Objects
      - **Represents:** Reactions and their coefficients.

      - **First Stoichiometry Object:**
        - **`name: Citrate Synthase Reaction`**
          - **Type:** String
          - **Represents:** Reaction name.
        - **`coefficient: 1`**
          - **Type:** Number
          - **Represents:** Stoichiometric coefficient.

  - **`mass_charge:`**
    - **Type:** Object
    - **Represents:** Mass and charge properties.

    - **`molecular_weight: 809.57`**
      - **Type:** Number
      - **Represents:** Molecular weight in g/mol.

    - **`charge: -1`**
      - **Type:** Number/String
      - **Represents:** Net charge.

  - **`visualization:`**
    - **Type:** Object
    - **Represents:** Links to visual structural data.

    - **`structure_2D: "structures/acetyl_coa_2d.png"`**
      - **Type:** String
      - **Represents:** Path or URL to a 2D structure image.

    - **`structure_3D: "structures/acetyl_coa_3d.pdb"`**
      - **Type:** String
      - **Represents:** Path or URL to a 3D structure file.

  - **`energy_metrics:`**
    - **Type:** Object
    - **Represents:** Energy-related metrics.

    - **`ATP_yield: 3`**
      - **Type:** Number
      - **Represents:** Amount of ATP produced or consumed.

  - **`experimental_data:`**
    - **Type:** Object
    - **Represents:** Empirical data for validation.

    - **`concentration: 5.0`**
      - **Type:** Number
      - **Represents:** Measured concentration in mM.

    - **`reference: "Smith et al., 2020"`**
      - **Type:** String
      - **Represents:** Citation for the data.

---

### **Best Practices for Schema Implementation**

1. **Use Descriptive Names:**
   - Ensure metabolite names are clear and standardized to avoid confusion.
   - Consider using IUPAC names or common biological nomenclature.

2. **Maintain Consistent Units:**
   - Always specify units for numerical values to maintain clarity.
   - Use consistent units across all metabolite entries.

3. **Modularize Complex Structures:**
   - For extensive simulations, consider breaking down the YAML into modular files (e.g., separate files for core metabolites, electron carriers, etc.) and include them as needed.

4. **Leverage YAML Features:**
   - Utilize YAML anchors and aliases to reduce redundancy for common structures.
   - Example:
     ```yaml
     defaults: &defaults
       concentration:
         default: 10
         unit: mM
         range:
           min: 0.1
           max: 100
       localization:
         compartments:
           - Cytosol

     metabolites:
       Acetyl-CoA:
         <<: *defaults
         type: Core Krebs Cycle Intermediate
         description: ...
         meta:
           molecular_formula: ...
           # Additional fields
       Citrate:
         <<: *defaults
         type: Core Krebs Cycle Intermediate
         description: ...
         meta:
           molecular_formula: ...
           # Additional fields
     ```

5. **Validate Against Biological Databases:**
   - Cross-reference metabolite data with databases like **KEGG**, **MetaCyc**, or **ChEBI** to ensure accuracy and completeness.

6. **Document and Comment:**
   - Use comments within the YAML file to explain complex or non-intuitive fields.
   - Maintain external documentation for comprehensive understanding.

7. **Handle Optional Fields Gracefully:**
   - Design your simulation to handle missing or optional fields without errors.
   - Use default values or conditional logic where appropriate.

8. **Version Control:**
   - Use version control systems (e.g., Git) to track changes to your YAML schema and metabolite entries, facilitating collaboration and rollback if necessary.

---

### **Extending the Schema**

Depending on the complexity and requirements of your simulation, you might need to incorporate additional attributes or adjust existing ones. Here are some suggestions:

1. **Metabolite Interchangeability:**
   - Allow for multiple forms or derivatives of a metabolite (e.g., phosphorylated forms).

2. **Environmental Sensitivity:**
   - Incorporate more detailed environmental factors affecting metabolite behavior (e.g., ionic strength, presence of inhibitors).

3. **Genetic Variability:**
   - Link genetic variations or mutations to changes in metabolite concentrations or reaction kinetics.

4. **Pathway Branching:**
   - Represent metabolites that participate in multiple pathways with different roles.

5. **Temporal Dynamics:**
   - Include time-dependent changes in metabolite concentrations or fluxes.

---

### **Conclusion**

This schema description provides a structured and detailed framework for representing metabolites in your `metabolites.yml` file. By adhering to this schema, you can ensure that your simulation accurately captures the complex interactions and dynamics of cellular metabolism. Proper documentation and consistent data entry will facilitate easier maintenance, scalability, and collaboration as your project evolves.

If you have any specific questions or need further customization of this schema to better fit your simulation needs, feel free to ask!