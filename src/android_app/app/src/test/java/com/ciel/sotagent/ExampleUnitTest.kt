package com.ciel.sotagent

import org.junit.Assert.assertEquals
import org.junit.Test

class ExampleUnitTest {
    @Test
    fun appName_isStable() {
        assertEquals("com.ciel.sotagent", BuildConfig.APPLICATION_ID)
    }
}
