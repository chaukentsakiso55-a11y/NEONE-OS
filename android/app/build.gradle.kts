plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

fun secret(name: String) = providers.gradleProperty(name).orElse("")

val geminiKey = secret("NEON_GEMINI_API_KEY")
val xKiroKey = secret("NEON_XKIRO_API_KEY")
val anthropicKey = secret("NEON_ANTHROPIC_API_KEY")
val openAiKey = secret("NEON_OPENAI_API_KEY")
val groqKey = secret("NEON_GROQ_API_KEY")
val openRouterKey = secret("NEON_OPENROUTER_API_KEY")

android {
    namespace = "com.darthwolf.neonos"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.darthwolf.neonos"
        minSdk = 26
        targetSdk = 35
        versionCode = 1
        versionName = "0.1.0-alpha"

        buildConfigField("String", "GEMINI_API_KEY", "\"" + geminiKey.get().replace("\"", "\\\"") + "\"")
        buildConfigField("String", "XKIRO_API_KEY", "\"" + xKiroKey.get().replace("\"", "\\\"") + "\"")
        buildConfigField("String", "ANTHROPIC_API_KEY", "\"" + anthropicKey.get().replace("\"", "\\\"") + "\"")
        buildConfigField("String", "OPENAI_API_KEY", "\"" + openAiKey.get().replace("\"", "\\\"") + "\"")
        buildConfigField("String", "GROQ_API_KEY", "\"" + groqKey.get().replace("\"", "\\\"") + "\"")
        buildConfigField("String", "OPENROUTER_API_KEY", "\"" + openRouterKey.get().replace("\"", "\\\"") + "\"")
    }

    buildFeatures {
        buildConfig = true
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }

    packaging {
        resources.excludes += "/META-INF/{AL2.0,LGPL2.1}"
    }
}

dependencies {
    implementation("androidx.core:core-ktx:1.15.0")
    implementation("androidx.appcompat:appcompat:1.7.0")
    implementation("androidx.webkit:webkit:1.12.1")
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.9.0")
}
