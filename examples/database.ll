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
@"g_total_registros" = internal global i64 0
define void @"put"(i64 %".1", i64 %".2")
{
put_entry:
  %"chave" = alloca i64
  store i64 %".1", i64* %"chave"
  %"valor" = alloca i64
  store i64 %".2", i64* %"valor"
  br label %"put_body"
put_body:
  %".7" = bitcast [5 x i8]* @"str_0" to i8*
  %"chave_load" = load i64, i64* %"chave"
  %".8" = bitcast [4 x i8]* @"str_1" to i8*
  %"num_to_str" = alloca [64 x i8]
  %"num_to_str_ptr" = bitcast [64 x i8]* %"num_to_str" to i8*
  %"num_to_str_call" = call i32 (i8*, i64, i8*, ...) @"snprintf"(i8* %"num_to_str_ptr", i64 64, i8* %".8", i64 %"chave_load")
  %"sconcat_len1" = call i64 @"strlen"(i8* %".7")
  %"sconcat_len2" = call i64 @"strlen"(i8* %"num_to_str_ptr")
  %"sconcat_sum" = add i64 %"sconcat_len1", %"sconcat_len2"
  %"sconcat_total" = add i64 %"sconcat_sum", 1
  %"sconcat_buf" = call i8* @"GC_malloc"(i64 %"sconcat_total")
  %"sconcat_cpy" = call i8* @"strcpy"(i8* %"sconcat_buf", i8* %".7")
  %"sconcat_cat" = call i8* @"strcat"(i8* %"sconcat_buf", i8* %"num_to_str_ptr")
  %".9" = bitcast [2 x i8]* @"str_2" to i8*
  %"sconcat_len1.1" = call i64 @"strlen"(i8* %"sconcat_buf")
  %"sconcat_len2.1" = call i64 @"strlen"(i8* %".9")
  %"sconcat_sum.1" = add i64 %"sconcat_len1.1", %"sconcat_len2.1"
  %"sconcat_total.1" = add i64 %"sconcat_sum.1", 1
  %"sconcat_buf.1" = call i8* @"GC_malloc"(i64 %"sconcat_total.1")
  %"sconcat_cpy.1" = call i8* @"strcpy"(i8* %"sconcat_buf.1", i8* %"sconcat_buf")
  %"sconcat_cat.1" = call i8* @"strcat"(i8* %"sconcat_buf.1", i8* %".9")
  %"valor_load" = load i64, i64* %"valor"
  %".10" = bitcast [4 x i8]* @"str_3" to i8*
  %"num_to_str.1" = alloca [64 x i8]
  %"num_to_str_ptr.1" = bitcast [64 x i8]* %"num_to_str.1" to i8*
  %"num_to_str_call.1" = call i32 (i8*, i64, i8*, ...) @"snprintf"(i8* %"num_to_str_ptr.1", i64 64, i8* %".10", i64 %"valor_load")
  %"sconcat_len1.2" = call i64 @"strlen"(i8* %"sconcat_buf.1")
  %"sconcat_len2.2" = call i64 @"strlen"(i8* %"num_to_str_ptr.1")
  %"sconcat_sum.2" = add i64 %"sconcat_len1.2", %"sconcat_len2.2"
  %"sconcat_total.2" = add i64 %"sconcat_sum.2", 1
  %"sconcat_buf.2" = call i8* @"GC_malloc"(i64 %"sconcat_total.2")
  %"sconcat_cpy.2" = call i8* @"strcpy"(i8* %"sconcat_buf.2", i8* %"sconcat_buf.1")
  %"sconcat_cat.2" = call i8* @"strcat"(i8* %"sconcat_buf.2", i8* %"num_to_str_ptr.1")
  %".11" = bitcast [2 x i8]* @"str_4" to i8*
  %"sconcat_len1.3" = call i64 @"strlen"(i8* %"sconcat_buf.2")
  %"sconcat_len2.3" = call i64 @"strlen"(i8* %".11")
  %"sconcat_sum.3" = add i64 %"sconcat_len1.3", %"sconcat_len2.3"
  %"sconcat_total.3" = add i64 %"sconcat_sum.3", 1
  %"sconcat_buf.3" = call i8* @"GC_malloc"(i64 %"sconcat_total.3")
  %"sconcat_cpy.3" = call i8* @"strcpy"(i8* %"sconcat_buf.3", i8* %"sconcat_buf.2")
  %"sconcat_cat.3" = call i8* @"strcat"(i8* %"sconcat_buf.3", i8* %".11")
  %"log_entry" = alloca i8*
  store i8* %"sconcat_buf.3", i8** %"log_entry"
  %".13" = bitcast [11 x i8]* @"str_5" to i8*
  %"log_entry_load" = load i8*, i8** %"log_entry"
  %".14" = bitcast [2 x i8]* @"str_6" to i8*
  %"wf_fopen" = call i8* @"fopen"(i8* %".13", i8* %".14")
  %"wf_fputs" = call i32 @"fputs"(i8* %"log_entry_load", i8* %"wf_fopen")
  %"wf_fclose" = call i32 @"fclose"(i8* %"wf_fopen")
  %"chave_load.1" = load i64, i64* %"chave"
  %"alloc_size" = mul i64 100, 8
  %"alloc_call" = call i8* @"GC_malloc"(i64 %"alloc_size")
  %"g_total_registros_load" = load i64, i64* @"g_total_registros"
  %"idx_ptr" = getelementptr i8, i8* %"alloc_call", i64 %"g_total_registros_load"
  %"elem_trunc" = trunc i64 %"chave_load.1" to i8
  store i8 %"elem_trunc", i8* %"idx_ptr"
  %"valor_load.1" = load i64, i64* %"valor"
  %"alloc_size.1" = mul i64 100, 8
  %"alloc_call.1" = call i8* @"GC_malloc"(i64 %"alloc_size.1")
  %"g_total_registros_load.1" = load i64, i64* @"g_total_registros"
  %"add" = add i64 %"g_total_registros_load.1", 1
  %"idx_ptr.1" = getelementptr i8, i8* %"alloc_call.1", i64 %"add"
  %"elem_trunc.1" = trunc i64 %"valor_load.1" to i8
  store i8 %"elem_trunc.1", i8* %"idx_ptr.1"
  %"g_total_registros_load.2" = load i64, i64* @"g_total_registros"
  %"add.1" = add i64 %"g_total_registros_load.2", 2
  store i64 %"add.1", i64* @"g_total_registros"
  ret void
}

define i64 @"get"(i64 %".1")
{
get_entry:
  %"chave" = alloca i64
  store i64 %".1", i64* %"chave"
  br label %"get_body"
get_body:
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"while_cond"
while_cond:
  %"i_load" = load i64, i64* %"i"
  %"g_total_registros_load" = load i64, i64* @"g_total_registros"
  %"icmp" = icmp slt i64 %"i_load", %"g_total_registros_load"
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %"alloc_size" = mul i64 100, 8
  %"alloc_call" = call i8* @"GC_malloc"(i64 %"alloc_size")
  %"i_load.1" = load i64, i64* %"i"
  %".8" = getelementptr i8, i8* %"alloc_call", i64 %"i_load.1"
  %"ptr_idx_load" = load i8, i8* %".8"
  %"idx_sext" = sext i8 %"ptr_idx_load" to i64
  %"chave_load" = load i64, i64* %"chave"
  %"icmp.1" = icmp eq i64 %"idx_sext", %"chave_load"
  br i1 %"icmp.1", label %"if_then", label %"if_else"
while_end:
  %"neg" = sub i64 0, 1
  ret i64 %"neg"
if_then:
  %"alloc_size.1" = mul i64 100, 8
  %"alloc_call.1" = call i8* @"GC_malloc"(i64 %"alloc_size.1")
  %"i_load.2" = load i64, i64* %"i"
  %"add" = add i64 %"i_load.2", 1
  %".10" = getelementptr i8, i8* %"alloc_call.1", i64 %"add"
  %"ptr_idx_load.1" = load i8, i8* %".10"
  %"idx_sext.1" = sext i8 %"ptr_idx_load.1" to i64
  ret i64 %"idx_sext.1"
if_else:
  br label %"if_end"
if_end:
  %"i_load.3" = load i64, i64* %"i"
  %"add.1" = add i64 %"i_load.3", 2
  store i64 %"add.1", i64* %"i"
  br label %"while_cond"
}

define void @"recover"()
{
recover_entry:
  br label %"recover_body"
recover_body:
  %".3" = bitcast [34 x i8]* @"str_7" to i8*
  %".4" = bitcast [3 x i8]* @"str_8" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".4", i8* %".3")
  %".5" = bitcast [2 x i8]* @"str_9" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".5")
  %".6" = bitcast [11 x i8]* @"str_10" to i8*
  %".7" = bitcast [2 x i8]* @"str_11" to i8*
  %"rf_fopen" = call i8* @"fopen"(i8* %".6", i8* %".7")
  %"rf_fp_int" = ptrtoint i8* %"rf_fopen" to i64
  %"rf_is_null" = icmp eq i64 %"rf_fp_int", 0
  br i1 %"rf_is_null", label %"rf_null", label %"rf_ok"
rf_null:
  %".9" = bitcast [1 x i8]* @"str_12" to i8*
  br label %"rf_end"
rf_ok:
  %"rf_seek_end" = call i32 @"fseek"(i8* %"rf_fopen", i64 0, i32 2)
  %"rf_size" = call i64 @"ftell"(i8* %"rf_fopen")
  %"rf_seek_set" = call i32 @"fseek"(i8* %"rf_fopen", i64 0, i32 0)
  %"rf_size_plus" = add i64 %"rf_size", 1
  %"rf_buf" = call i8* @"GC_malloc"(i64 %"rf_size_plus")
  %"rf_fread" = call i64 @"fread"(i8* %"rf_buf", i64 1, i64 %"rf_size", i8* %"rf_fopen")
  %"rf_end_ptr" = getelementptr i8, i8* %"rf_buf", i64 %"rf_size"
  store i8 0, i8* %"rf_end_ptr"
  %"rf_fclose" = call i32 @"fclose"(i8* %"rf_fopen")
  br label %"rf_end"
rf_end:
  %"rf_result" = phi  i8* [%".9", %"rf_null"], [%"rf_buf", %"rf_ok"]
  %"dados" = alloca i8*
  store i8* %"rf_result", i8** %"dados"
  %"dados_load" = load i8*, i8** %"dados"
  %"len_str" = call i64 @"strlen"(i8* %"dados_load")
  %"tamanho" = alloca i64
  store i64 %"len_str", i64* %"tamanho"
  %"tamanho_load" = load i64, i64* %"tamanho"
  %"icmp" = icmp eq i64 %"tamanho_load", 0
  br i1 %"icmp", label %"if_then", label %"if_else"
if_then:
  %".16" = bitcast [57 x i8]* @"str_13" to i8*
  %".17" = bitcast [3 x i8]* @"str_14" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".17", i8* %".16")
  %".18" = bitcast [2 x i8]* @"str_15" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".18")
  ret void
if_else:
  br label %"if_end"
if_end:
  %".21" = bitcast [50 x i8]* @"str_16" to i8*
  %".22" = bitcast [3 x i8]* @"str_17" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".22", i8* %".21")
  %".23" = bitcast [2 x i8]* @"str_18" to i8*
  %"print_nl.2" = call i32 (i8*, ...) @"printf"(i8* %".23")
  %".24" = bitcast [16 x i8]* @"str_19" to i8*
  %".25" = bitcast [3 x i8]* @"str_20" to i8*
  %"print_call.3" = call i32 (i8*, ...) @"printf"(i8* %".25", i8* %".24")
  %"tamanho_load.1" = load i64, i64* %"tamanho"
  %".26" = bitcast [2 x i8]* @"str_21" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".26")
  %".27" = bitcast [4 x i8]* @"str_22" to i8*
  %"print_call.4" = call i32 (i8*, ...) @"printf"(i8* %".27", i64 %"tamanho_load.1")
  %".28" = bitcast [7 x i8]* @"str_23" to i8*
  %".29" = bitcast [2 x i8]* @"str_24" to i8*
  %"print_sep.1" = call i32 (i8*, ...) @"printf"(i8* %".29")
  %".30" = bitcast [3 x i8]* @"str_25" to i8*
  %"print_call.5" = call i32 (i8*, ...) @"printf"(i8* %".30", i8* %".28")
  %".31" = bitcast [2 x i8]* @"str_26" to i8*
  %"print_nl.3" = call i32 (i8*, ...) @"printf"(i8* %".31")
  ret void
}

define i32 @"main"(i32 %".1", i8** %".2")
{
main_entry:
  call void @"GC_init"()
  store i32 %".1", i32* @"__lumina_argc"
  store i8** %".2", i8*** @"__lumina_argv"
  br label %"main_body"
main_body:
  %".7" = bitcast [27 x i8]* @"str_27" to i8*
  %".8" = bitcast [3 x i8]* @"str_28" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".8", i8* %".7")
  %".9" = bitcast [2 x i8]* @"str_29" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".9")
  call void @"recover"()
  call void @"put"(i64 1, i64 100)
  call void @"put"(i64 2, i64 200)
  call void @"put"(i64 3, i64 300)
  %"get_call" = call i64 @"get"(i64 2)
  %"res" = alloca i64
  store i64 %"get_call", i64* %"res"
  %"res_load" = load i64, i64* %"res"
  %"neg" = sub i64 0, 1
  %"icmp" = icmp ne i64 %"res_load", %"neg"
  br i1 %"icmp", label %"if_then", label %"if_else"
if_then:
  %".12" = bitcast [31 x i8]* @"str_30" to i8*
  %".13" = bitcast [3 x i8]* @"str_31" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".13", i8* %".12")
  %"res_load.1" = load i64, i64* %"res"
  %".14" = bitcast [2 x i8]* @"str_32" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".14")
  %".15" = bitcast [4 x i8]* @"str_33" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".15", i64 %"res_load.1")
  %".16" = bitcast [2 x i8]* @"str_34" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".16")
  br label %"if_end"
if_else:
  %".18" = bitcast [29 x i8]* @"str_35" to i8*
  %".19" = bitcast [3 x i8]* @"str_36" to i8*
  %"print_call.3" = call i32 (i8*, ...) @"printf"(i8* %".19", i8* %".18")
  %".20" = bitcast [2 x i8]* @"str_37" to i8*
  %"print_nl.2" = call i32 (i8*, ...) @"printf"(i8* %".20")
  br label %"if_end"
if_end:
  %".22" = bitcast [67 x i8]* @"str_38" to i8*
  %".23" = bitcast [3 x i8]* @"str_39" to i8*
  %"print_call.4" = call i32 (i8*, ...) @"printf"(i8* %".23", i8* %".22")
  %".24" = bitcast [2 x i8]* @"str_40" to i8*
  %"print_nl.3" = call i32 (i8*, ...) @"printf"(i8* %".24")
  %"ret_trunc" = trunc i64 0 to i32
  ret i32 %"ret_trunc"
}

@"__lumina_argc" = global i32 0
@"__lumina_argv" = global i8** null
declare i64 @"remove"(i8* %".1")

define i64 @"deletar_arquivo"(i8* %".1")
{
deletar_arquivo_entry:
  %"path" = alloca i8*
  store i8* %".1", i8** %"path"
  br label %"deletar_arquivo_body"
deletar_arquivo_body:
  %"path_load" = load i8*, i8** %"path"
  %"remove_call" = call i64 @"remove"(i8* %"path_load")
  ret i64 %"remove_call"
}

@"str_0" = constant [5 x i8] c"PUT \00"
@"str_1" = constant [4 x i8] c"%ld\00"
@"str_2" = constant [2 x i8] c",\00"
@"str_3" = constant [4 x i8] c"%ld\00"
@"str_4" = constant [2 x i8] c"\0a\00"
@"str_5" = constant [11 x i8] c"lumina.wal\00"
declare i8* @"fopen"(i8* %".1", i8* %".2")

declare i32 @"fputs"(i8* %".1", i8* %".2")

declare i32 @"fclose"(i8* %".1")

@"str_6" = constant [2 x i8] c"w\00"
@"str_7" = constant [34 x i8] c"Iniciando recupera\c3\a7\c3\a3o do WAL...\00"
@"str_8" = constant [3 x i8] c"%s\00"
@"str_9" = constant [2 x i8] c"\0a\00"
@"str_10" = constant [11 x i8] c"lumina.wal\00"
declare i32 @"fseek"(i8* %".1", i64 %".2", i32 %".3")

declare i64 @"ftell"(i8* %".1")

declare i64 @"fread"(i8* %".1", i64 %".2", i64 %".3", i8* %".4")

@"str_11" = constant [2 x i8] c"r\00"
@"str_12" = constant [1 x i8] c"\00"
@"str_13" = constant [57 x i8] c"Banco de dados vazio. Nenhuma recupera\c3\a7\c3\a3o necess\c3\a1ria.\00"
@"str_14" = constant [3 x i8] c"%s\00"
@"str_15" = constant [2 x i8] c"\0a\00"
@"str_16" = constant [50 x i8] c"Dados recuperados do log: (simula\c3\a7\c3\a3o de replay)\00"
@"str_17" = constant [3 x i8] c"%s\00"
@"str_18" = constant [2 x i8] c"\0a\00"
@"str_19" = constant [16 x i8] c"Tamanho do log:\00"
@"str_20" = constant [3 x i8] c"%s\00"
@"str_21" = constant [2 x i8] c" \00"
@"str_22" = constant [4 x i8] c"%ld\00"
@"str_23" = constant [7 x i8] c"bytes.\00"
@"str_24" = constant [2 x i8] c" \00"
@"str_25" = constant [3 x i8] c"%s\00"
@"str_26" = constant [2 x i8] c"\0a\00"
@"str_27" = constant [27 x i8] c"\f0\9f\9a\80 LuminaDB iniciando...\00"
@"str_28" = constant [3 x i8] c"%s\00"
@"str_29" = constant [2 x i8] c"\0a\00"
@"str_30" = constant [31 x i8] c"\e2\9c\85 Chave 2 encontrada. Valor:\00"
@"str_31" = constant [3 x i8] c"%s\00"
@"str_32" = constant [2 x i8] c" \00"
@"str_33" = constant [4 x i8] c"%ld\00"
@"str_34" = constant [2 x i8] c"\0a\00"
@"str_35" = constant [29 x i8] c"\e2\9d\8c Chave 2 n\c3\a3o encontrada.\00"
@"str_36" = constant [3 x i8] c"%s\00"
@"str_37" = constant [2 x i8] c"\0a\00"
@"str_38" = constant [67 x i8] c"\f0\9f\92\be Banco de dados em execu\c3\a7\c3\a3o. Dados persistidos em lumina.wal\00"
@"str_39" = constant [3 x i8] c"%s\00"
@"str_40" = constant [2 x i8] c"\0a\00"