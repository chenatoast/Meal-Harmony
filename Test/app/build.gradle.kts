plugins {
    id("com.android.application")
    id("com.chaquo.python")
}

android {
    namespace = "com.example.test"
    compileSdk = 34

    flavorDimensions += "pyVersion"
    productFlavors {
        create("py310") { dimension = "pyVersion" }
    }

    defaultConfig {
        applicationId = "com.example.test"
        minSdk = 28
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"

        ndk {
            // On Apple silicon, you can omit x86_64.
            abiFilters += listOf("arm64-v8a", "x86_64")
        }
    }

    sourceSets {
        getByName("main") {
            assets.srcDirs("src/main/python")
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_1_8
        targetCompatibility = JavaVersion.VERSION_1_8
    }
}



dependencies {

    implementation("androidx.appcompat:appcompat:1.7.0")
    implementation("com.google.android.material:material:1.12.0")
    implementation("androidx.constraintlayout:constraintlayout:2.1.4")
    testImplementation("junit:junit:4.13.2")
    androidTestImplementation("androidx.test.ext:junit:1.2.1")
    androidTestImplementation("androidx.test.espresso:espresso-core:3.6.1")
}
chaquopy {
    defaultConfig {
        buildPython("C:/Users/mail/AppData/Local/Programs/Python/Python310/python.exe")
        version = "3.10"

        pip {
            // A requirement specifier, with or without a version number:
            install("numpy")
            install("pandas")
            install("scikit-learn")
        }
    }

    productFlavors {
        getByName("py310") { version = "3.10" }
    }

    sourceSets {

    }
}