; ModuleID = "lumina_module"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = ""

%"Option" = type {i32, i64}
%"Result" = type {i32, i64}
%"Usuario" = type {i64}
declare i32 @"printf"(i8* %".1", ...)

declare i8* @"GC_malloc"(i64 %".1")

declare void @"GC_init"()

declare void @"GC_free"(i8* %".1")

declare i8* @"strcpy"(i8* %".1", i8* %".2")

declare i8* @"strcat"(i8* %".1", i8* %".2")

declare i64 @"strlen"(i8* %".1")

declare i32 @"snprintf"(i8* %".1", i64 %".2", i8* %".3", ...)

declare i8* @"strstr"(i8* %".1", i8* %".2")

declare i32 @"strncmp"(i8* %".1", i8* %".2", i64 %".3")

declare i64 @"atoi"(i8* %".1")

declare i32 @"strcmp"(i8* %".1", i8* %".2")

declare i8* @"strncpy"(i8* %".1", i8* %".2", i64 %".3")

@"stdin" = external global i8*
@"stdout" = external global i8*
@"stderr" = external global i8*
define i32 @"main"(i32 %".1", i8** %".2")
{
main_entry:
  call void @"GC_init"()
  store i32 %".1", i32* @"__lumina_argc"
  store i8** %".2", i8*** @"__lumina_argv"
  br label %"main_body"
main_body:
  %"u" = alloca %"Usuario"*
  %"u_storage_raw" = call i8* @"GC_malloc"(i64 8)
  %"u_storage" = bitcast i8* %"u_storage_raw" to %"Usuario"*
  store %"Usuario" {i64 0}, %"Usuario"* %"u_storage"
  store %"Usuario"* %"u_storage", %"Usuario"** %"u"
  %"u_load" = load %"Usuario"*, %"Usuario"** %"u"
  %"id_ptr" = getelementptr %"Usuario", %"Usuario"* %"u_load", i32 0, i32 0
  store i64 42, i64* %"id_ptr"
  %"u_load.1" = load %"Usuario"*, %"Usuario"** %"u"
  %".10" = getelementptr %"Usuario", %"Usuario"* %"u_load.1", i32 0, i32 0
  %"id_load" = load i64, i64* %".10"
  %"id1" = alloca i64
  store i64 %"id_load", i64* %"id1"
  %".12" = bitcast [11 x i8]* @"str_0" to i8*
  %".13" = bitcast [3 x i8]* @"str_1" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".13", i8* %".12")
  %"id1_load" = load i64, i64* %"id1"
  %".14" = bitcast [2 x i8]* @"str_2" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".14")
  %".15" = bitcast [4 x i8]* @"str_3" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".15", i64 %"id1_load")
  %".16" = bitcast [2 x i8]* @"str_4" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".16")
  %"u_load.2" = load %"Usuario"*, %"Usuario"** %"u"
  %"safe_nav_isnull" = icmp eq %"Usuario"* %"u_load.2", null
  br i1 %"safe_nav_isnull", label %"safe_nav_null", label %"safe_nav_ok"
safe_nav_null:
  br label %"safe_nav_end"
safe_nav_ok:
  %".19" = getelementptr %"Usuario", %"Usuario"* %"u_load.2", i32 0, i32 0
  %"id_load.1" = load i64, i64* %".19"
  br label %"safe_nav_end"
safe_nav_end:
  %"safe_nav_result" = phi  i64 [0, %"safe_nav_null"], [%"id_load.1", %"safe_nav_ok"]
  %"id2" = alloca i64
  store i64 %"safe_nav_result", i64* %"id2"
  %".22" = bitcast [19 x i8]* @"str_5" to i8*
  %".23" = bitcast [3 x i8]* @"str_6" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".23", i8* %".22")
  %"id2_load" = load i64, i64* %"id2"
  %".24" = bitcast [2 x i8]* @"str_7" to i8*
  %"print_sep.1" = call i32 (i8*, ...) @"printf"(i8* %".24")
  %".25" = bitcast [4 x i8]* @"str_8" to i8*
  %"print_call.3" = call i32 (i8*, ...) @"printf"(i8* %".25", i64 %"id2_load")
  %".26" = bitcast [2 x i8]* @"str_9" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".26")
  %"u_nulo" = alloca %"Usuario"*
  %"ptr_cast" = bitcast i8* null to %"Usuario"*
  store %"Usuario"* %"ptr_cast", %"Usuario"** %"u_nulo"
  %"u_nulo_load" = load %"Usuario"*, %"Usuario"** %"u_nulo"
  %"cmp_ptr_bitcast" = bitcast i8* null to %"Usuario"*
  %"icmp" = icmp eq %"Usuario"* %"u_nulo_load", %"cmp_ptr_bitcast"
  br i1 %"icmp", label %"if_then", label %"if_else"
if_then:
  %".29" = bitcast [14 x i8]* @"str_10" to i8*
  %".30" = bitcast [3 x i8]* @"str_11" to i8*
  %"print_call.4" = call i32 (i8*, ...) @"printf"(i8* %".30", i8* %".29")
  %".31" = bitcast [2 x i8]* @"str_12" to i8*
  %"print_nl.2" = call i32 (i8*, ...) @"printf"(i8* %".31")
  br label %"if_end"
if_else:
  br label %"if_end"
if_end:
  %"u_nulo_load.1" = load %"Usuario"*, %"Usuario"** %"u_nulo"
  %"safe_nav_isnull.1" = icmp eq %"Usuario"* %"u_nulo_load.1", null
  br i1 %"safe_nav_isnull.1", label %"safe_nav_null.1", label %"safe_nav_ok.1"
safe_nav_null.1:
  br label %"safe_nav_end.1"
safe_nav_ok.1:
  %".36" = getelementptr %"Usuario", %"Usuario"* %"u_nulo_load.1", i32 0, i32 0
  %"id_load.2" = load i64, i64* %".36"
  br label %"safe_nav_end.1"
safe_nav_end.1:
  %"safe_nav_result.1" = phi  i64 [0, %"safe_nav_null.1"], [%"id_load.2", %"safe_nav_ok.1"]
  %"id3" = alloca i64
  store i64 %"safe_nav_result.1", i64* %"id3"
  %".39" = bitcast [22 x i8]* @"str_13" to i8*
  %".40" = bitcast [3 x i8]* @"str_14" to i8*
  %"print_call.5" = call i32 (i8*, ...) @"printf"(i8* %".40", i8* %".39")
  %"id3_load" = load i64, i64* %"id3"
  %".41" = bitcast [2 x i8]* @"str_15" to i8*
  %"print_sep.2" = call i32 (i8*, ...) @"printf"(i8* %".41")
  %".42" = bitcast [4 x i8]* @"str_16" to i8*
  %"print_call.6" = call i32 (i8*, ...) @"printf"(i8* %".42", i64 %"id3_load")
  %".43" = bitcast [2 x i8]* @"str_17" to i8*
  %"print_nl.3" = call i32 (i8*, ...) @"printf"(i8* %".43")
  %"ret_trunc" = trunc i64 0 to i32
  ret i32 %"ret_trunc"
}

@"__lumina_argc" = global i32 0
@"__lumina_argv" = global i8** null
@"str_0" = constant [11 x i8] c"ID normal:\00"
@"str_1" = constant [3 x i8] c"%s\00"
@"str_2" = constant [2 x i8] c" \00"
@"str_3" = constant [4 x i8] c"%ld\00"
@"str_4" = constant [2 x i8] c"\0a\00"
@"str_5" = constant [19 x i8] c"ID seguro (u?.id):\00"
@"str_6" = constant [3 x i8] c"%s\00"
@"str_7" = constant [2 x i8] c" \00"
@"str_8" = constant [4 x i8] c"%ld\00"
@"str_9" = constant [2 x i8] c"\0a\00"
@"str_10" = constant [14 x i8] c"u_nulo \c3\a9 nil\00"
@"str_11" = constant [3 x i8] c"%s\00"
@"str_12" = constant [2 x i8] c"\0a\00"
@"str_13" = constant [22 x i8] c"ID seguro (nulo?.id):\00"
@"str_14" = constant [3 x i8] c"%s\00"
@"str_15" = constant [2 x i8] c" \00"
@"str_16" = constant [4 x i8] c"%ld\00"
@"str_17" = constant [2 x i8] c"\0a\00"