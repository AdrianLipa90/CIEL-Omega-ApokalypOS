package com.ciel.sotagent

import org.junit.Assert.assertTrue
import org.junit.Test

class ExampleUnitTest {
    @Test
    fun appName_isStable() {
        assertTrue(BuildConfig.APPLICATION_ID.startsWith("com.ciel.sotagent"))
    }
}
