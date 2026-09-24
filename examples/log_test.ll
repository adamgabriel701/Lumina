; ModuleID = "lumina_module"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = ""

%"Option" = type {i32, i64}
%"Result" = type {i32, i64}
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
@"g__log_min_level" = internal global i64 1
define i32 @"main"(i32 %".1", i8** %".2")
{
main_entry:
  call void @"GC_init"()
  store i32 %".1", i32* @"__lumina_argc"
  store i8** %".2", i8*** @"__lumina_argv"
  br label %"main_body"
main_body:
  %".7" = bitcast [30 x i8]* @"str_0" to i8*
  %".8" = bitcast [3 x i8]* @"str_1" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".8", i8* %".7")
  %".9" = bitcast [2 x i8]* @"str_2" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".9")
  call void @"set_level"(i64 1)
  %".10" = bitcast [27 x i8]* @"str_3" to i8*
  call void @"log_debug"(i8* %".10")
  %".11" = bitcast [13 x i8]* @"str_4" to i8*
  call void @"log_info"(i8* %".11")
  %".12" = bitcast [13 x i8]* @"str_5" to i8*
  call void @"log_warn"(i8* %".12")
  %".13" = bitcast [14 x i8]* @"str_6" to i8*
  call void @"log_error"(i8* %".13")
  %".14" = bitcast [1 x i8]* @"str_7" to i8*
  %".15" = bitcast [3 x i8]* @"str_8" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".15", i8* %".14")
  %".16" = bitcast [2 x i8]* @"str_9" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".16")
  %".17" = bitcast [21 x i8]* @"str_10" to i8*
  %".18" = bitcast [3 x i8]* @"str_11" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".18", i8* %".17")
  %".19" = bitcast [2 x i8]* @"str_12" to i8*
  %"print_nl.2" = call i32 (i8*, ...) @"printf"(i8* %".19")
  call void @"set_level"(i64 0)
  %".20" = bitcast [20 x i8]* @"str_13" to i8*
  call void @"log_debug"(i8* %".20")
  %".21" = bitcast [25 x i8]* @"str_14" to i8*
  call void @"log_info"(i8* %".21")
  %".22" = bitcast [10 x i8]* @"str_15" to i8*
  call void @"log_warn"(i8* %".22")
  %".23" = bitcast [11 x i8]* @"str_16" to i8*
  call void @"log_error"(i8* %".23")
  %".24" = bitcast [1 x i8]* @"str_17" to i8*
  %".25" = bitcast [3 x i8]* @"str_18" to i8*
  %"print_call.3" = call i32 (i8*, ...) @"printf"(i8* %".25", i8* %".24")
  %".26" = bitcast [2 x i8]* @"str_19" to i8*
  %"print_nl.3" = call i32 (i8*, ...) @"printf"(i8* %".26")
  %".27" = bitcast [21 x i8]* @"str_20" to i8*
  %".28" = bitcast [3 x i8]* @"str_21" to i8*
  %"print_call.4" = call i32 (i8*, ...) @"printf"(i8* %".28", i8* %".27")
  %".29" = bitcast [2 x i8]* @"str_22" to i8*
  %"print_nl.4" = call i32 (i8*, ...) @"printf"(i8* %".29")
  call void @"set_level"(i64 3)
  %".30" = bitcast [15 x i8]* @"str_23" to i8*
  call void @"log_debug"(i8* %".30")
  %".31" = bitcast [14 x i8]* @"str_24" to i8*
  call void @"log_info"(i8* %".31")
  %".32" = bitcast [14 x i8]* @"str_25" to i8*
  call void @"log_warn"(i8* %".32")
  %".33" = bitcast [18 x i8]* @"str_26" to i8*
  call void @"log_error"(i8* %".33")
  %".34" = bitcast [1 x i8]* @"str_27" to i8*
  %".35" = bitcast [3 x i8]* @"str_28" to i8*
  %"print_call.5" = call i32 (i8*, ...) @"printf"(i8* %".35", i8* %".34")
  %".36" = bitcast [2 x i8]* @"str_29" to i8*
  %"print_nl.5" = call i32 (i8*, ...) @"printf"(i8* %".36")
  %".37" = bitcast [20 x i8]* @"str_30" to i8*
  %".38" = bitcast [3 x i8]* @"str_31" to i8*
  %"print_call.6" = call i32 (i8*, ...) @"printf"(i8* %".38", i8* %".37")
  %".39" = bitcast [2 x i8]* @"str_32" to i8*
  %"print_nl.6" = call i32 (i8*, ...) @"printf"(i8* %".39")
  %".40" = bitcast [14 x i8]* @"str_33" to i8*
  %".41" = bitcast [3 x i8]* @"str_34" to i8*
  %"print_call.7" = call i32 (i8*, ...) @"printf"(i8* %".41", i8* %".40")
  %"get_level_call" = call i64 @"get_level"()
  %".42" = bitcast [2 x i8]* @"str_35" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".42")
  %".43" = bitcast [4 x i8]* @"str_36" to i8*
  %"print_call.8" = call i32 (i8*, ...) @"printf"(i8* %".43", i64 %"get_level_call")
  %".44" = bitcast [2 x i8]* @"str_37" to i8*
  %"print_nl.7" = call i32 (i8*, ...) @"printf"(i8* %".44")
  %"ret_trunc" = trunc i64 0 to i32
  ret i32 %"ret_trunc"
}

@"__lumina_argc" = global i32 0
@"__lumina_argv" = global i8** null
define void @"set_level"(i64 %".1")
{
set_level_entry:
  %"level" = alloca i64
  store i64 %".1", i64* %"level"
  br label %"set_level_body"
set_level_body:
  %"level_load" = load i64, i64* %"level"
  store i64 %"level_load", i64* @"g__log_min_level"
  ret void
}

define i64 @"get_level"()
{
get_level_entry:
  br label %"get_level_body"
get_level_body:
  %"g__log_min_level_load" = load i64, i64* @"g__log_min_level"
  ret i64 %"g__log_min_level_load"
}

define void @"_log"(i64 %".1", i8* %".2", i8* %".3")
{
_log_entry:
  %"level" = alloca i64
  store i64 %".1", i64* %"level"
  %"prefix" = alloca i8*
  store i8* %".2", i8** %"prefix"
  %"msg" = alloca i8*
  store i8* %".3", i8** %"msg"
  br label %"_log_body"
_log_body:
  %"level_load" = load i64, i64* %"level"
  %"g__log_min_level_load" = load i64, i64* @"g__log_min_level"
  %"icmp" = icmp sge i64 %"level_load", %"g__log_min_level_load"
  br i1 %"icmp", label %"if_then", label %"if_else"
if_then:
  %"prefix_load" = load i8*, i8** %"prefix"
  %".10" = bitcast [3 x i8]* @"str_38" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".10", i8* %"prefix_load")
  %"msg_load" = load i8*, i8** %"msg"
  %".11" = bitcast [2 x i8]* @"str_39" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".11")
  %".12" = bitcast [3 x i8]* @"str_40" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".12", i8* %"msg_load")
  %".13" = bitcast [2 x i8]* @"str_41" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".13")
  br label %"if_end"
if_else:
  br label %"if_end"
if_end:
  ret void
}

define void @"log_debug"(i8* %".1")
{
log_debug_entry:
  %"msg" = alloca i8*
  store i8* %".1", i8** %"msg"
  br label %"log_debug_body"
log_debug_body:
  %".5" = bitcast [8 x i8]* @"str_42" to i8*
  %"msg_load" = load i8*, i8** %"msg"
  call void @"_log"(i64 0, i8* %".5", i8* %"msg_load")
  ret void
}

define void @"log_info"(i8* %".1")
{
log_info_entry:
  %"msg" = alloca i8*
  store i8* %".1", i8** %"msg"
  br label %"log_info_body"
log_info_body:
  %".5" = bitcast [8 x i8]* @"str_43" to i8*
  %"msg_load" = load i8*, i8** %"msg"
  call void @"_log"(i64 1, i8* %".5", i8* %"msg_load")
  ret void
}

define void @"log_warn"(i8* %".1")
{
log_warn_entry:
  %"msg" = alloca i8*
  store i8* %".1", i8** %"msg"
  br label %"log_warn_body"
log_warn_body:
  %".5" = bitcast [8 x i8]* @"str_44" to i8*
  %"msg_load" = load i8*, i8** %"msg"
  call void @"_log"(i64 2, i8* %".5", i8* %"msg_load")
  ret void
}

define void @"log_error"(i8* %".1")
{
log_error_entry:
  %"msg" = alloca i8*
  store i8* %".1", i8** %"msg"
  br label %"log_error_body"
log_error_body:
  %".5" = bitcast [8 x i8]* @"str_45" to i8*
  %"msg_load" = load i8*, i8** %"msg"
  call void @"_log"(i64 3, i8* %".5", i8* %"msg_load")
  ret void
}

@"str_0" = constant [30 x i8] c"=== n\c3\advel INFO (padr\c3\a3o) ===\00"
@"str_1" = constant [3 x i8] c"%s\00"
@"str_2" = constant [2 x i8] c"\0a\00"
@"str_3" = constant [27 x i8] c"debug (n\c3\a3o deve aparecer)\00"
@"str_4" = constant [13 x i8] c"info aparece\00"
@"str_5" = constant [13 x i8] c"warn aparece\00"
@"str_6" = constant [14 x i8] c"error aparece\00"
@"str_7" = constant [1 x i8] c"\00"
@"str_8" = constant [3 x i8] c"%s\00"
@"str_9" = constant [2 x i8] c"\0a\00"
@"str_10" = constant [21 x i8] c"=== n\c3\advel DEBUG ===\00"
@"str_11" = constant [3 x i8] c"%s\00"
@"str_12" = constant [2 x i8] c"\0a\00"
@"str_13" = constant [20 x i8] c"agora debug aparece\00"
@"str_14" = constant [25 x i8] c"info continua aparecendo\00"
@"str_15" = constant [10 x i8] c"warn idem\00"
@"str_16" = constant [11 x i8] c"error idem\00"
@"str_17" = constant [1 x i8] c"\00"
@"str_18" = constant [3 x i8] c"%s\00"
@"str_19" = constant [2 x i8] c"\0a\00"
@"str_20" = constant [21 x i8] c"=== n\c3\advel ERROR ===\00"
@"str_21" = constant [3 x i8] c"%s\00"
@"str_22" = constant [2 x i8] c"\0a\00"
@"str_23" = constant [15 x i8] c"debug filtrado\00"
@"str_24" = constant [14 x i8] c"info filtrado\00"
@"str_25" = constant [14 x i8] c"warn filtrado\00"
@"str_26" = constant [18 x i8] c"s\c3\b3 error aparece\00"
@"str_27" = constant [1 x i8] c"\00"
@"str_28" = constant [3 x i8] c"%s\00"
@"str_29" = constant [2 x i8] c"\0a\00"
@"str_30" = constant [20 x i8] c"=== get_level() ===\00"
@"str_31" = constant [3 x i8] c"%s\00"
@"str_32" = constant [2 x i8] c"\0a\00"
@"str_33" = constant [14 x i8] c"n\c3\advel atual:\00"
@"str_34" = constant [3 x i8] c"%s\00"
@"str_35" = constant [2 x i8] c" \00"
@"str_36" = constant [4 x i8] c"%ld\00"
@"str_37" = constant [2 x i8] c"\0a\00"
@"str_38" = constant [3 x i8] c"%s\00"
@"str_39" = constant [2 x i8] c" \00"
@"str_40" = constant [3 x i8] c"%s\00"
@"str_41" = constant [2 x i8] c"\0a\00"
@"str_42" = constant [8 x i8] c"[DEBUG]\00"
@"str_43" = constant [8 x i8] c"[INFO] \00"
@"str_44" = constant [8 x i8] c"[WARN] \00"
@"str_45" = constant [8 x i8] c"[ERROR]\00"