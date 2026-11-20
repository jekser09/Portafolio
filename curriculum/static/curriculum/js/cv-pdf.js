/**
 * Generador vectorial de Hoja de Vida en PDF en el navegador (Client-Side Offloading).
 * Utiliza carga diferida (lazy loading) de pdfmake v0.2.12 y soporta dos disposiciones:
 * 2 columnas con barra lateral y 1 columna lineal optimizada para sistemas ATS.
 * Cargado con atributo 'defer' — sin envoltorios DOMContentLoaded ni window.onload.
 */

const PDFMAKE_CDN_URL =
  "https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.2.12/pdfmake.min.js";
const VFS_FONTS_CDN_URL =
  "https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.2.12/vfs_fonts.min.js";

const PRIMARY_NAVY = "#1C3D63";
const SIDEBAR_BG = "#F1F5F9";
const TEXT_DARK = "#0F172A";
const TEXT_BODY = "#1E293B";
const TEXT_SKILLS = "#111827";

let pdfMakeLoadPromise = null;

/**
 * Inserta y carga dinámicamente un script externo por su URL.
 * Si un intento previo falló, reemplaza el nodo defectuoso para permitir reintentos.
 * @param {string} src - URL del script externo.
 * @returns {Promise<void>}
 */
function loadExternalScript(src) {
  return new Promise((resolve, reject) => {
    const existingScript = document.querySelector(`script[src="${src}"]`);
    if (existingScript) {
      if (existingScript.dataset.loaded === "true") {
        resolve();
        return;
      }
      existingScript.remove();
    }

    const script = document.createElement("script");
    script.src = src;
    script.async = true;

    script.addEventListener("load", () => {
      script.dataset.loaded = "true";
      resolve();
    });

    script.addEventListener("error", () => {
      script.remove();
      reject(new Error(`No se pudo cargar la librería externa: ${src}`));
    });

    (document.head || document.documentElement).appendChild(script);
  });
}

/**
 * Carga secuencialmente pdfmake y vfs_fonts con caché en memoria.
 * Reinicia la promesa si ocurre un error para permitir reintentos posteriores.
 * @returns {Promise<object>} Instancia global de window.pdfMake.
 */
function loadPdfMake() {
  if (typeof window.pdfMake?.createPdf === "function" && window.pdfMake?.vfs) {
    return Promise.resolve(window.pdfMake);
  }

  if (!pdfMakeLoadPromise) {
    pdfMakeLoadPromise = loadExternalScript(PDFMAKE_CDN_URL)
      .then(() => loadExternalScript(VFS_FONTS_CDN_URL))
      .then(() => {
        if (typeof window.pdfMake?.createPdf !== "function") {
          throw new Error(
            "pdfmake se cargó, pero window.pdfMake.createPdf no está disponible."
          );
        }
        return window.pdfMake;
      })
      .catch((error) => {
        pdfMakeLoadPromise = null;
        throw error;
      });
  }

  return pdfMakeLoadPromise;
}

/**
 * Normaliza texto multilínea dividiendo párrafos por doble salto de línea
 * y colapsando saltos simples internos para lograr un justificado uniforme.
 * @param {string} text - Texto de entrada.
 * @returns {string[]} Lista de párrafos limpios no vacíos.
 */
function splitNormalizedParagraphs(text) {
  if (typeof text !== "string") {
    return [];
  }

  return text
    .replace(/\r\n/g, "\n")
    .split(/\n\s*\n/)
    .map((paragraph) => paragraph.replace(/\s*\n\s*/g, " ").trim())
    .filter(Boolean);
}

/**
 * Limpia una URL para mostrarla sin esquema ni prefijo www ni barra final.
 * @param {string} url - URL completa original.
 * @returns {string} URL legible para mostrar en el encabezado.
 */
function cleanUrlDisplay(url) {
  if (typeof url !== "string") {
    return "";
  }

  return url
    .trim()
    .replace(/^https?:\/\/(www\.)?/i, "")
    .replace(/\/+$/, "");
}

/**
 * Construye un encabezado de sección con línea inferior sólida en azul marino.
 * @param {string} title - Título de la sección.
 * @returns {object} Nodo de tabla compatible con pdfmake.
 */
function buildSectionHeading(title) {
  return {
    table: {
      widths: ["*"],
      body: [
        [
          {
            text: String(title || "").toUpperCase(),
            bold: true,
            fontSize: 10.5,
            color: PRIMARY_NAVY,
          },
        ],
      ],
    },
    layout: {
      hLineWidth: (i, node) => (i === node.table.body.length ? 1.2 : 0),
      vLineWidth: () => 0,
      hLineColor: () => PRIMARY_NAVY,
      paddingLeft: () => 0,
      paddingRight: () => 0,
      paddingTop: () => 0,
      paddingBottom: () => 3,
    },
    margin: [0, 8, 0, 5],
  };
}

/**
 * Construye el banner superior del CV con nombre completo y enlaces de contacto.
 * @param {object} profile - Datos del perfil profesional.
 * @returns {object} Nodo de tabla compatible con pdfmake.
 */
function buildHeaderBanner(profile) {
  const safeProfile = profile || {};
  const contactItems = [];

  const email = (safeProfile.email || "").trim();
  if (email) {
    contactItems.push({
      text: email,
      link: `mailto:${email}`,
      color: "#FFFFFF",
    });
  }

  const phone = (safeProfile.phone || "").trim();
  if (phone) {
    contactItems.push({
      text: phone,
      color: "#FFFFFF",
    });
  }

  const location = (safeProfile.location || "").trim();
  if (location) {
    contactItems.push({
      text: location,
      link: `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(location)}`,
      color: "#FFFFFF",
    });
  }

  const githubUrl = (safeProfile.github_url || "").trim();
  if (githubUrl) {
    contactItems.push({
      text: cleanUrlDisplay(githubUrl),
      link: githubUrl,
      color: "#FFFFFF",
    });
  }

  const linkedinUrl = (safeProfile.linkedin_url || "").trim();
  if (linkedinUrl) {
    contactItems.push({
      text: cleanUrlDisplay(linkedinUrl),
      link: linkedinUrl,
      color: "#FFFFFF",
    });
  }

  const contactLine = [];
  contactItems.forEach((item, index) => {
    if (index > 0) {
      contactLine.push("  |  ");
    }
    contactLine.push(item);
  });

  const cellStack = [
    {
      text: (safeProfile.full_name || "").toUpperCase(),
      fontSize: 19,
      bold: true,
      color: "#FFFFFF",
      alignment: "center",
      margin: [0, 0, 0, 4],
    },
  ];

  if (contactLine.length > 0) {
    cellStack.push({
      text: contactLine,
      fontSize: 9,
      color: "#FFFFFF",
      alignment: "center",
    });
  }

  return {
    table: {
      widths: ["*"],
      body: [
        [
          {
            fillColor: PRIMARY_NAVY,
            stack: cellStack,
          },
        ],
      ],
    },
    layout: {
      hLineWidth: () => 0,
      vLineWidth: () => 0,
      paddingLeft: () => 14,
      paddingRight: () => 14,
      paddingTop: () => 12,
      paddingBottom: () => 12,
    },
    margin: [0, 0, 0, 10],
  };
}

/**
 * Construye los bloques de párrafos justificados del perfil profesional.
 * @param {object} profile - Datos del perfil profesional.
 * @returns {object[]} Arreglo de nodos de texto para pdfmake.
 */
function buildProfileBlocks(profile) {
  const paragraphs = splitNormalizedParagraphs(profile?.bio);

  return paragraphs.map((paragraph, index) => ({
    text: paragraph,
    alignment: "justify",
    fontSize: 9.5,
    lineHeight: 1.25,
    color: TEXT_BODY,
    margin: [0, 0, 0, index < paragraphs.length - 1 ? 5 : 2],
  }));
}

/**
 * Construye los bloques vectoriales de experiencia laboral y sus logros.
 * @param {object[]} experiences - Lista de experiencias laborales.
 * @returns {object[]} Arreglo de nodos para pdfmake.
 */
function buildExperienceBlocks(experiences) {
  if (!Array.isArray(experiences)) {
    return [];
  }

  const blocks = [];
  experiences.forEach((exp) => {
    const role = exp?.role || "";
    const period = exp?.period || "";
    const roleLine = period ? `${role} | ${period}` : role;

    blocks.push({
      text: roleLine,
      bold: true,
      fontSize: 10,
      color: TEXT_DARK,
      margin: [0, 4, 0, 1],
    });

    blocks.push({
      text: `Empresa: ${(exp?.company || "").toUpperCase()}`,
      bold: true,
      fontSize: 9.5,
      color: PRIMARY_NAVY,
      margin: [0, 0, 0, 3],
    });

    if (Array.isArray(exp?.highlights) && exp.highlights.length > 0) {
      const items = exp.highlights
        .map((highlight) => splitNormalizedParagraphs(highlight?.description).join(" "))
        .filter(Boolean);

      if (items.length > 0) {
        blocks.push({
          ul: items,
          fontSize: 9.2,
          lineHeight: 1.22,
          alignment: "justify",
          color: TEXT_BODY,
          margin: [0, 0, 0, 5],
        });
      }
    }
  });

  return blocks;
}

/**
 * Construye los bloques de formación académica.
 * @param {object[]} education - Registros de educación.
 * @returns {object[]} Arreglo de nodos para pdfmake.
 */
function buildEducationBlocks(education) {
  if (!Array.isArray(education)) {
    return [];
  }

  const blocks = [];
  education.forEach((edu) => {
    const statusLabel = edu?.is_in_progress ? "En curso" : "Culminado";
    const yearValue = edu?.year_completed ? `${edu.year_completed} ` : "";

    blocks.push({
      text: `${edu?.degree || ""} | ${yearValue}(${statusLabel})`,
      bold: true,
      fontSize: 9.5,
      color: TEXT_DARK,
      margin: [0, 3, 0, 1],
    });

    blocks.push({
      text: edu?.institution || "",
      bold: true,
      fontSize: 9.2,
      color: PRIMARY_NAVY,
      margin: [0, 0, 0, 4],
    });
  });

  return blocks;
}

/**
 * Construye los bloques de referencias laborales.
 * @param {object[]} references - Referencias laborales visibles.
 * @returns {object[]} Arreglo de nodos para pdfmake.
 */
function buildReferencesBlocks(references) {
  if (!Array.isArray(references) || references.length === 0) {
    return [];
  }

  const blocks = [];
  references.forEach((ref) => {
    const name = ref?.name || "";
    const phone = ref?.phone || "";
    const headerLine = phone ? `${name} | ${phone}` : name;

    blocks.push({
      text: headerLine,
      bold: true,
      fontSize: 9.5,
      color: TEXT_DARK,
      margin: [0, 3, 0, 1],
    });

    blocks.push({
      text: ref?.role || "",
      bold: true,
      fontSize: 9.2,
      color: PRIMARY_NAVY,
      margin: [0, 0, 0, 4],
    });
  });

  return blocks;
}

/**
 * Filtra las categorías de habilidades que poseen al menos un elemento.
 * @param {object[]} skillsByCategory - Categorías con sus habilidades.
 * @returns {object[]} Categorías no vacías.
 */
function getNonEmptySkillCategories(skillsByCategory) {
  if (!Array.isArray(skillsByCategory)) {
    return [];
  }

  return skillsByCategory.filter(
    (category) => Array.isArray(category?.skills) && category.skills.length > 0
  );
}

/**
 * Construye la definición de documento en formato lineal de 1 columna optimizado para ATS.
 * @param {object} cvData - Payload estructurado del CV.
 * @returns {object} Definición de documento para pdfmake.
 */
function buildAtsDocDefinition(cvData) {
  const { profile, skills_by_category, experiences, education, references } =
    cvData || {};
  const nonEmptyCategories = getNonEmptySkillCategories(skills_by_category);

  const stackBlocks = nonEmptyCategories.map((category) => ({
    text: [
      { text: `${category.name}: `, bold: true, color: PRIMARY_NAVY },
      {
        text: category.skills.map((skill) => skill.name).join(", "),
        color: TEXT_SKILLS,
      },
    ],
    fontSize: 9.5,
    lineHeight: 1.25,
    margin: [0, 1.5, 0, 1.5],
  }));

  const content = [
    buildHeaderBanner(profile),
    buildSectionHeading("PERFIL PROFESIONAL"),
    ...buildProfileBlocks(profile),
    buildSectionHeading("STACK TECNOLÓGICO"),
    ...stackBlocks,
    buildSectionHeading("EXPERIENCIA LABORAL"),
    ...buildExperienceBlocks(experiences),
    buildSectionHeading("FORMACIÓN ACADÉMICA"),
    ...buildEducationBlocks(education),
  ];

  if (Array.isArray(references) && references.length > 0) {
    content.push(
      buildSectionHeading("REFERENCIAS"),
      ...buildReferencesBlocks(references)
    );
  }

  return {
    pageSize: "A4",
    pageMargins: [36, 30, 36, 30],
    defaultStyle: {
      font: "Roboto",
      fontSize: 9.5,
      color: TEXT_BODY,
    },
    content,
  };
}

/**
 * Construye la definición de documento asimétrico en 2 columnas.
 * @param {object} cvData - Payload estructurado del CV.
 * @returns {object} Definición de documento para pdfmake.
 */
function buildTwoColDocDefinition(cvData) {
  const { profile, skills_by_category, experiences, education, references } =
    cvData || {};
  const nonEmptyCategories = getNonEmptySkillCategories(skills_by_category);

  const leftStack = [buildSectionHeading("STACK TECNOLÓGICO")];

  if (nonEmptyCategories.length > 0) {
    leftStack.push({
      table: {
        widths: [64, "*"],
        body: nonEmptyCategories.map((category) => [
          {
            text: category.name,
            bold: true,
            fontSize: 8.5,
            color: PRIMARY_NAVY,
          },
          {
            text: category.skills.map((skill) => skill.name).join(", "),
            fontSize: 8.5,
            color: TEXT_SKILLS,
          },
        ]),
      },
      layout: {
        hLineWidth: () => 0,
        vLineWidth: () => 0,
        paddingLeft: () => 0,
        paddingRight: (col) => (col === 0 ? 4 : 0),
        paddingTop: () => 2,
        paddingBottom: () => 2,
      },
    });
  }

  leftStack.push(
    buildSectionHeading("FORMACIÓN ACADÉMICA"),
    ...buildEducationBlocks(education)
  );

  if (Array.isArray(references) && references.length > 0) {
    leftStack.push(
      buildSectionHeading("REFERENCIAS"),
      ...buildReferencesBlocks(references)
    );
  }

  const rightStack = [
    buildSectionHeading("PERFIL PROFESIONAL"),
    ...buildProfileBlocks(profile),
    buildSectionHeading("EXPERIENCIA LABORAL"),
    ...buildExperienceBlocks(experiences),
  ];

  return {
    pageSize: "A4",
    pageMargins: [32, 28, 32, 28],
    defaultStyle: {
      font: "Roboto",
      fontSize: 9.2,
      color: TEXT_BODY,
    },
    content: [
      buildHeaderBanner(profile),
      {
        table: {
          widths: [185, "*"],
          body: [
            [
              {
                fillColor: SIDEBAR_BG,
                stack: leftStack,
              },
              {
                stack: rightStack,
              },
            ],
          ],
        },
        layout: {
          hLineWidth: () => 0,
          vLineWidth: () => 0,
          paddingLeft: (col) => (col === 0 ? 10 : 14),
          paddingRight: (col) => (col === 0 ? 10 : 4),
          paddingTop: () => 10,
          paddingBottom: () => 10,
        },
      },
    ],
  };
}

/**
 * Construye un nombre de archivo ASCII seguro para la descarga del CV en PDF.
 * @param {object} profile - Datos del perfil profesional.
 * @param {string} layoutMode - Disposición seleccionada ("ats" o "two-col").
 * @returns {string} Nombre de archivo con extensión .pdf.
 */
function buildPdfFilename(profile, layoutMode) {
  const rawName = (profile?.full_name || "CV").trim();
  const asciiName = rawName
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-zA-Z0-9]+/g, "_")
    .replace(/^_+|_+$/g, "");

  const safeName = asciiName || "CV";
  const suffix = layoutMode === "ats" ? "ATS" : "2_Columnas";

  return `HV_${safeName}_${suffix}.pdf`;
}

/**
 * Genera y descarga el PDF vectorial del CV según la disposición activa.
 * @param {object} cvData - Payload estructurado proveniente de #cv-data.
 * @param {string} layoutMode - Disposición activa: "two-col" o "ats".
 * @returns {Promise<string>} Nombre del archivo PDF generado.
 */
window.generateCvPdf = async function generateCvPdf(cvData, layoutMode) {
  if (!cvData || typeof cvData !== "object") {
    throw new Error("Los datos del CV no son válidos para generar el PDF.");
  }

  const layout = layoutMode === "ats" ? "ats" : "two-col";
  const pdfMake = await loadPdfMake();

  const docDefinition =
    layout === "ats"
      ? buildAtsDocDefinition(cvData)
      : buildTwoColDocDefinition(cvData);

  const fullName = (cvData.profile?.full_name || "").trim();
  const layoutLabel = layout === "ats" ? "ATS" : "2 Columnas";

  docDefinition.info = {
    title: fullName
      ? `Hoja de Vida - ${fullName} (${layoutLabel})`
      : `Hoja de Vida (${layoutLabel})`,
    author: fullName,
  };

  const filename = buildPdfFilename(cvData.profile, layout);
  pdfMake.createPdf(docDefinition).download(filename);

  return filename;
};
